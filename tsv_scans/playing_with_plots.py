import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import csv

import uncertainties as unc
from decimal import Decimal as dec
from uncertainties import ufloat, unumpy as unp
from scipy.optimize import curve_fit
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.lines as mlines
from matplotlib import colors, cm, _cm_listed
import matplotlib.pylab as pl

import os
import logging
import path
import re
from numpy.core.defchararray import endswith
from uncertainties.unumpy.core import uarray
from __builtin__ import file



class TSV_res_meas_analysis(object):
    
    '''
    Via map gives the horizontal position of every via with respect to the center of the leftmost wirebond pad (#1)
    on the upper side of the FE
    '''
    
    via_map = {'via1':-169, 'via2':59, 'via3':1090, 'via4':1467, 'via5':1390, 'via6':2067, 'via7':2367, 'via8':3575, 'via9':3725, 'via10':5375,
               'via11':5675, 'via12':8675, 'via13':8825, 'via14':8963, 'via15':11800, 'via16':11950, 'via17':14275, 'via18':16312, 'via19':16550,
               'via20':16700, 'via21':17750, 'via22':17900, 'via23':18050, 'via24':18200, 'via25':19336, 'via26':19719} 
    
    
    def __init__(self, outformat='.pdf'):
        
        self.outformat=outformat
        self.outfile = ''
        self.error=False
        
    
    def load_file_no_err(self,path):
            if not os.path.split(path)[1].split('.')[1] == 'csv':
                raise IOError('Wrong filetype!')
            self.dirpath = os.path.split(path)[0]
            self.filename = os.path.split(path)[1].split('.')[0]
            self.outfile = os.path.join(os.path.split(path)[0], self.filename)
            title_parts = re.split('(\d+)', self.filename)
#             print title_parts
            if len(title_parts) > 3 :
                self.title1 = title_parts[0] + title_parts[1] + title_parts[2].split('-')[0] #os.path.split(path)[1].split('V')[0]
            else:
                self.title1 = title_parts[0] + title_parts[1]
#             print self.title1

            self.f = os.path.split(path)[1]    
                    
            x,y = [], []
            with open(path, 'rb') as datafile:
                linereader = csv.reader(datafile, delimiter=',', quotechar='"')
                _ = linereader.next()
                frow = linereader.next()

                x.append(float(frow[0]))
                y.append(float(frow[1]))
                for row in linereader:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
    
            return x, y, self.title1
    


    def load_file(self,path):
        
        
        if not os.path.split(path)[1].split('.')[1] == 'csv':
            raise IOError('Wrong filetype!')
        self.dirpath = os.path.split(path)[0]
        self.outfile = os.path.join(os.path.split(path)[0], (os.path.split(path)[1].split('.')[0]))
        self.title = os.path.split(path)[1].split('.')[0]
        
        self.f = os.path.split(path)[1]    
        
        x1,y1,z1 =     [], [], []
        xerr = 0.0002 + 0.0005
        yerr = 0.0005 + 0.0005
        xrel = 0.0012
        yrel = 0.003
        with open(path, 'rb') as datafile:
            linereader = csv.reader(datafile, delimiter=',', quotechar='"')
            _ = linereader.next()
            frow = linereader.next()
            
            ''' introducing syst. uncertainties here: voltage: 0.12 % + 200microV , current: 0.3 % + 500microA
                for std_dev one stepsize (500micro and 500microA) has been estimated
            '''

            x1.append(ufloat(frow[0], float(frow[0])*xrel + xerr))
            y1.append(ufloat(frow[1], float(frow[1])*yrel + yerr))
            z1.append(x1[-1]/y1[-1])
            for row in linereader:
                x1.append(ufloat(row[0], float(row[0])*xrel + xerr))
                y1.append(ufloat(row[1], float(row[1])*yrel + yerr))
                z1.append(x1[-1]/y1[-1])

        return x1[5:], y1[5:], z1[5:]

    
#     def plot_single_via(self, x, y, z, p0, fit, voltage=True):
    def plot_single_via(self, datafile, p0,fit,voltage=True):
        
#         x1,x2 = self.unpack_uncertainties(x)
#         y1,y2 = self.unpack_uncertainties(y)
#         z1,z2 = self.unpack_uncertainties(z)
        
#         name = os.path.split(datafile)[1].split('-')[0] + os.path.split(datafile)[1].split('-')[1]
        x1, y1, z1 = np.absolute(np.loadtxt(datafile, delimiter = ',', skiprows = 1, unpack = 'true'))
        
        path_list = datafile.split(os.sep)
        title = 'Resistance of ' + path_list[5] + ' ' +  path_list[7].split('-')[0]

        first = 0
        ymax = 1.1*np.amax(z1)
        
        plt.clf()
        plt.ylim(0,ymax)     
        

        m = np.mean(z1)
        print ('mean resistance: %r Ohm' % m)
#         m = np.round(np.mean(z[first:]),4)    # use this line instead the upper one, in case of sm 2410 (first 40 values are rubbish)
        if voltage is True:
            plt.xlabel('Voltage [V]')
            xmax = 1.1*np.amax(x1)
            plt.xlim(0,xmax)
#             mpl.rcParams['legend.handlelength'] = 0
            plt.plot(x1,z1, '.', markersize = 3,label=' Data \n mean = %.3f $\Omega$' %m)
#             plt.errorbar(x1, z1, yerr = z2, errorevery = 4, color = 'blue', marker = 'o', markersize = 2,label=' Data \n mean = %s' %m)          
        else :
            plt.xlabel('Current [A]')
            xmax = 1.1*np.amax(y1)
            plt.xlim(0,xmax)
            plt.plot(y1,z1,label='Data  mean = %s' %m, marker = '.', color='blue')
#             plt.errorbar(y1, z1,yerr = z2)
        plt.ylabel('Resistance [Ohm]')
        if fit:
            p, _ =  curve_fit(self.fitfunction_line, x1[first:], z1[first:], p0) 
            plt.plot(self.fitfunction_line(x1[first:],*p), 'r',label='Fit')
#             print curve_fit(self.fitfunction_single_via, x, z, p0=(1,-1,10))
            print 'fit succesful: b = %r' % p[1]
#             except: 
#                 logging.error('Fit failed!') 
#         plt.text(0.1,0,'mean = %r' %np.round(np.mean(z[40:]),3))
        plt.title(title)
        plt.legend(loc='best', numpoints = 1)
        plt.grid()
#         box = AnchoredText('mean = %f' %np.round(np.mean(z[first:]),3), loc='right center')
#         ax = plt.axes()
#         ax.add_artist(box)        
        plt.savefig(datafile[:-4] + self.outformat)
        logging.info('RV file saved to %s' % (datafile[:-4] + self.outformat))
    
    
    def wirebond_corr(self, data, length_t, length_b, spec_res):
        r_via_top = length_t*spec_res
        r_via_bottom = length_b*spec_res
        total_r = r_via_bottom + r_via_top
        data_corr = np.subtract(data,total_r)    
        return data_corr, total_r    
    
    def zoom_single_via(self,x,y,z):  
          
        ymax = 1.03*np.amax(z)
        
        plt.cla()
        plt.ylim(0.3,ymax)     
        plt.title(self.title)
        plt.xlabel('Voltage [V]')
        xmax = 1.1*np.amax(x)
        plt.xlim(0,xmax)
        plt.plot(x,z, 'b.', markersize = 3,label='Data')
        plt.ylabel('Resistance [Ohm]')
        plt.grid()
        plt.savefig(self.outfile + '-zoom' + '.'+ self.outformat)
#         plt.show()    
    
    def fitfunction_line (self, x, *p):
        m,b = p
        return m*x+b
        
    def fitfunction_exp(self, x, *p):
        a, b, c = p
        return a*np.exp(b/x)+c # a*np.log(x)+ c*x**d +e #a*np.log(x*b) + x/c + d # a*np.exp(b/x)+c   #
              
    def fitfunction_poly(self,x,*p):
        a,b,c,d,e,f = p
        return a*x+b*x**2+c*x**3+d*x**4+e*x**5+f*x**5

    def fitfunction_gauss(self,x,*p):
        A,mu,sigma = p 
        return A*np.exp(-(x-mu)**2/(2*sigma**2))
      
    def histo_1_via(self, data, bins, c):
        
        plt.cla()
        plt.title(self.title)
        plt.grid()
        plt.hist(data, bins, range=[0, 1.5*np.amax(data)], color=c)
        plt.xlabel('Resistance [Ohm]')
        plt.ylabel('count [#]')
#         plt.text( 0.4, 25,'color = %r' % c )
        plt.savefig(self.outfile + '_histo' + '.' + self.outformat)
#         plt.show()
    
    def histo_FEs(self, data):
        
        os.chdir('/media/niko/data/TSV-measurements')
        x,x1 = self.unpack_uncertainties(data)
        print x
        plt.cla()
        plt.title(self.title)
        plt.ylim(0,9)
        plt.grid()
        plt.hist(x, bins = [0,0.5,1,2,3,4,5],color = 'blue' )
        plt.xlabel('Resistance [Ohm]')
        plt.ylabel('count [#]')
#         plt.text( 0.4, 25,'color = %r' % c )
        plt.savefig('histogram-of-mean-R-of' + str(len(x)) + '-FE.pdf')
        plt.show()
    
#     def plot_IV_curve(self, x, y, via_number, logy):
    def plot_IV_curve(self, datafile, logy):

        voltage, current, resistance = np.absolute(np.loadtxt(datafile, delimiter = ',', skiprows = 1, unpack = 'true'))
        
        path_list = datafile.split(os.sep)
        title = path_list[5] + ' ' +  path_list[7].split('-')[0]
        
        p, covariance =  curve_fit(self.fitfunction_line, voltage, current, p0=(0,0))
        
        textstr=('m = %.3e \n b = %.3e' %(p[0],p[1]))
        dummy = np.linspace(min(voltage), max(voltage), 100)
        
        plt.clf()
        plt.grid()
        plt.title(title + ' IV curve')
        plt.ylabel('Current [A]')
        plt.xlabel('Voltage [V]')
        
#         box = AnchoredText('m = %.3f \n b = %.5f' %(p[0],p[1]), bbox_to_anchor=(1,1),loc=1)      
#         ax = plt.axes()
#         ax.text(0.1, round(((ax.get_ylim()[1] + ax.get_ylim()[0])/2), 0), textstr, bbox=dict(boxstyle='square', facecolor='white'))
#         ax.add_artist(box)
        if not logy:
            file_name = 'fit'  
            plt.plot(voltage, current, '.', markersize = 5, label = 'data' )
            plt.plot(voltage, self.fitfunction_line(voltage, *p),'-', linewidth = 2, label = 'fit\n' + textstr)
#             plt.errorbar(voltage,current, voltage_std_dev, current_std_dev, 'b.', markersize = 3, label = 'data')
#             textstr=('R = %.2e $\Omega$' % (1/p[0])) # \n b = %.5f' %(1/p[0],p[1]))
#             leg = plt.legend(loc = 'best')
    #         plt.draw()
    #         loc = leg.get_window_extent().inverse_transformed(ax.transAxes)
    #         loc = leg.get_frame().get_bbox().bounds
    #         print loc
    #         leg_height = loc.p1[1]-loc.p1[0]
    #         print leg_height
    #         textbox = ax.text(-loc.p0[0]-0.05,-loc.p0[1]-0.05, textstr, bbox=dict(boxstyle='square', facecolor='white'))
            print 'covariance: %r' % (np.sqrt(np.diag(covariance)))
            print 'fit: %r' % p
        if logy:
            file_name = 'plot-log'
            plt.semilogy(voltage,current, label = 'data')
        plt.legend(loc = 'best')
        plt.savefig(datafile[:-4] + '-IV-' + file_name + self.outformat)
        logging.info('IV-plot saved to %s' % (datafile[:-4] + '-IV-' + file_name + self.outformat))
        
     
    def unpack_uncertainties (self, x):
    
        nominal,std_dev = [],[]

        for i in xrange(len(x)):
            nominal.append(unc.nominal_value(x[i]))
            std_dev.append(unc.std_dev(x[i]))
        
        return nominal,std_dev
        
    
    def get_resistance_from_fit(self, datafile):
        '''returns mean resistance from line fit and error on R for one via:
            the line fit gives slope m. From I=m*u + b and R=U/I it follows R=U/(U*m + b) for ervery point.
            The average R of the points and stat. uncertainty of R are calculated
            
            datafile is .csv file
        '''
        
        voltage, current, resistance = np.absolute(np.loadtxt(datafile, delimiter = ',', skiprows = 1, unpack = 'true'))
        p, covariance =  curve_fit(self.fitfunction_line, voltage, current, p0=(0,0))
        res = voltage/(voltage*p[0] + p[1])

        variance = np.sqrt(np.diag(covariance))
        m_err = variance[0] # this is a 1 sigma error of the fit (according to docu from curve_fit)
        deltaU = 3.54e-6 # np.std() determined from 100 voltage measurements for 20 10mV steps each
        deltaI = np.sqrt(np.square(variance[1]) + np.square(m_err/p[0]) + np.square(deltaU/voltage))
        unc = np.sqrt(np.square(deltaU/voltage) + np.square(deltaI/current))

        return np.mean(res), np.mean(unc), datafile
    
    
    
    def mean_per_FE(self,path, plotmarker):
                
        means, files, number = [],[],[]
        via = 1
        file_info = []
        for f in os.listdir(path):
            if f.endswith('.csv'):
#                 files.append(split.file('via','-')[1])
                files.append(os.path.split(f)[1]) #.split('via','-')[1]  
        logging.info('%r vias found, processing ...' %len(files))
        os.chdir(path)
        chip_number = os.path.split(os.path.split(path)[0])[1]

#         for i in xrange(len(files)):
#             file_info = re.split('(\d+)',files[i])
#             number.append(int(file_info[1]))
#             means.append(np.mean(self.load_file('via' + str(number[-1]) + '-' + file_info[3] + 'mamp-4wire.csv')[2])) #[50:]
#             
#         means1,means2 = self.unpack_uncertainties(means)
        for x in files:
            res, unc, datafile = self.get_resistance_from_fit(os.path.join(path,x))
            means.append((res,unc,float(datafile.split(os.sep)[-1].split('-')[0][3:]))) # last entry gives via number from datafile, needed for map
            
        means = np.array(means)
        means1 = means[:,0]
        means2 = means[:,1]
        
        yerr = means2
        if plotmarker==1:
            '''plotting histo and map''' 
            
            plt.cla()
            plt.title('vias on ' + chip_number)
            plt.grid()
            #plt.xlim(0,10**np.log(1e3))
            plt.hist(means1, bins = 10**np.linspace(np.log10(0.1), np.log(1e5),18)) #logarithmic binning 
            
            plt.gca().set_xscale('log')
            plt.xlabel('Mean resistance in Ohm')
            plt.ylabel('Count')
            plt.savefig(chip_number + '-resistance-histogram.pdf') 
            
            '''Plotting "map" (via index on x-axis) '''
            
            plt.cla()
            plt.title('Local distribution of vias on ' + chip_number)
            plt.xlabel('Via index')
            plt.ylabel('Resistance in Ohm')
            plt.grid()
            plt.xlim(0,27)
            plt.gca().set_yscale('log')
            labels = map(int, sorted(number,key = int))
            plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
#             plt.plot(number, means1, ' b.', markersize = 8, label = 'mean per via')
            plt.errorbar(number, means1, yerr=yerr, ls = 'None', marker = 'o', markersize = 3,label = 'mean per via')  
            plt.legend(loc = 'best', numpoints=1)
            plt.savefig(chip_number + '-distribution-map-scatter.pdf')
            plt.show()
        
        elif plotmarker==2:
            '''Plotting only real map (location of via in mm relative to lower left corner/ Pad 1) '''
            
            loc = {}
            x,y = [],[]
            for i in xrange (len(number)):
                loc.update({float(TSV_res_meas_analysis.via_map['via' + str(number[i])])/1000 : means[i]})
            for i in xrange (len(loc)):
                x = loc.keys()
                y = loc.values()
            y_nom, yerr = self.unpack_uncertainties(y)
            means = y
            plt.cla()    
            plt.plot(x,y_nom, 'o', markersize = 3, label = 'mean resistance per via')
#             plt.errorbar(x, y_nom, yerr=yerr, ls = 'None',marker = 'o', markersize = 3,label = 'mean resistance per via')

            plt.title('Local distribution of vias on ' + chip_number)
            plt.xlabel('Position on chip [mm]')
            plt.ylabel('Resistance [Ohm]')
            plt.grid()
            plt.xlim(-0.5,20.1)
            plt.gca().set_yscale('log')
            plt.legend(loc = 'best', numpoints=1)

            plt.savefig(chip_number + '-map-mm.pdf')            
            plt.show()
                    
        elif plotmarker==3:
            logging.info('calculating means only')
            loc = {}
            x,y = [],[]
            for i in xrange (len(means)):
#                 loc.update({float(TSV_res_meas_analysis.via_map['via' + str(number[i])])/1000 : means[i]})
                loc.update({float(TSV_res_meas_analysis.via_map['via' + str(int(means[i,:][2]))])/1000 : means[i,:][0]})
            for i in xrange (len(loc)):
                x = loc.keys()
                y = loc.values()
            means = y
            
        
        return {'via-numbers' : number, 'via-means' : means, 'chip-number' : chip_number, 'via-position':loc.keys()}   #numbers.append(re.split('(\d+)',files[i])[1])
                
    def plot_3_FE(self, mean1,mean2,mean3):   
    
        chip_numbers = [mean1[2], mean2[2], mean3[2] ]
        number = mean1[0]
        plt.cla()
        plt.title('Local distribution of via resistance on 3 FE ' )#+ mean1[2]  + ' , ' +  mean2[2] + ' and ' + mean3[2])
        plt.xlabel('via index')
        plt.ylabel('Resistance in Ohm')
        plt.grid()
        plt.xlim(0,27)
        plt.gca().set_yscale('log')
        labels = map(int, sorted(number,key = int))
        plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))        
        
        plt.plot(number, mean1[1], '.', label = mean1[2], markersize = 8)
        plt.plot(number, mean2[1], '.', label = mean2[2], markersize = 8)
        plt.plot(number, mean3[1],'.' , label = mean3[2], markersize = 8)
        
        plt.subplot(111).legend(bbox_to_anchor=(1.1, 1.1), numpoints = 1)
        #plt.legend(loc = 'best', numpoints=1)
        plt.savefig('combined-distribution-map.pdf')    
            
        
#         print number
#         if len(files)>10:
#             print files
#             for via in range(0,26):
#                 means.append(np.mean(self.load_file(files[via])[2]))
#                 via = split.files('via','-')[-1]
#                    
#         return means
     
    def plot_all_FE (self, mean_array, x_unit, yield_thr, destination):
        
        size = len(mean_array)
        os.chdir(destination)
        file_name = destination + '/histogram-data-of-' + str(size) + '-FE.csv'
        count = 0
        meancalc = []
        
        with PdfPages(file_name[:-3] + 'pdf') as output_pdf:
            
            fig = Figure()
            _ = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            ax.set_title('Spatial distribution of via resistance on %i FE' % size )
            ax.set_ylabel('Resistance [$\Omega$]')
            ax.grid()
            ax.set_yscale('log')
            ax.set_ylim(1e-2,1e10)
            means1,means2 = [],[]
            high = 0
            rel = 0
            total_count= 0
            legend_handler_values = []
            
            '''make colormap'''
            colormap = plt.cm.Spectral(np.linspace(0,1,size)) #Spectral
                            
            for i in xrange (len(mean_array)):
                means1,means2 = self.unpack_uncertainties(mean_array[i]['via-means'])
                count = 0
                for t in xrange (len(means1)):
                    if means1[t] <= 1:
                        count += 1
                        meancalc.append(means1[i])
                    else:
                        high +=1
                values, = ax.plot(mean_array[i]['via-'+ x_unit], means1, '.', color = colormap[i],label = str(mean_array[i]['chip-number']), markersize = 8, alpha = 1)
                legend_handler_values.append(values)
#                 plt.errorbar(mean_array[i]['via-'+ x_unit], means1, means2, marker = 'o',ls = 'None', label = str(mean_array[i]['chip-number']), markersize = 4)
                
                
                logging.info('plotting for FE %r' % mean_array[i]['chip-number'])
                print 'median of FE %s is: %s with %i vias connected' %(mean_array[i]['chip-number'],np.median(meancalc),count)
                total_count += count
                  
            if x_unit == 'position':
                ax.set_xlim(-0.5,20.5)
                ax.set_xlabel('Postion on chip [mm]')
            elif x_unit =='numbers':
                ax.set_xlim(0,27)  
                ax.set_xlabel('via index') 
                labels = map(int, sorted(mean_array[i]['via-numbers'],key = int))
                ax.set_xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
                
            rel = float(total_count)/float(total_count + high)# computing yield
            
#             plt.subplot(111).legend(loc = 'upper right', bbox_to_anchor=(0.98, 0.8,0.19,0.19), numpoints = 1, borderaxespad=0)#, mode = 'expand'
            box = ax.get_position()
            ax.set_position([box.x0 - box.width*0.02, box.y0 + box.height * 0.3,box.width*0.89, box.height * 0.75])
            threshold = ax.axhline(xmin = -0.1, xmax = 32,y = 1 , linewidth=2.5, color = 'crimson', linestyle = '--', label = 'threshold of %r $\Omega$' % yield_thr)
            lgd2 = ax.legend(handles = [threshold],bbox_to_anchor = (1.2,0.76),loc = 'center',frameon = False ,framealpha = 1)
            ax.add_artist(lgd2)
            lgd = ax.legend(handles = legend_handler_values,loc = 'lower center', bbox_to_anchor=(0.55,-0.59),numpoints  = 1,ncol = 5,fancybox = True)

            props = dict(boxstyle='round', facecolor='white', alpha=0.2)
            text = ax.text(1.03,0.99, 'number of vias: %r   \nconnected: %i \nyield: %2.0f %%\n\n\n' % (total_count + high,total_count,rel*100),verticalalignment='top',transform=ax.transAxes,bbox=props)

            output_pdf.savefig(fig, bbox_extra_artists = (text,lgd),bbox_inches = 'tight')
     
            '''now plotting histogram '''
            
            histo_array,histo_data, mean_values,mean_std_devs, low_mean,res_high, res_low = [], [], [],[],[], 0, 0
            
            fig = Figure()
            _ = FigureCanvas(fig)
            ax = fig.add_subplot(111)
                    
            with open(file_name, 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                f.writerow(['Resistance [ohm]']) 
 
                for i in xrange(len(mean_array)):
                    histo_array.append(mean_array[i]['via-means'])
                    count = 0
                    for b in xrange(len(histo_array[i])): 
                        histo_data.append(histo_array[i][b])
                        if abs(histo_data[-1]) <=1:
                            meancalc.append(histo_data[-1])
                            count +=1
#                         print histo_data[-1], type(histo_data[-1])
                        f.writerow([unc.nominal_value(histo_data[-1]),unc.std_dev(histo_data[-1])])
                        if abs(histo_array[i][b]) <= yield_thr :
                            low_mean.append(histo_array[i][b])
                            res_low += 1
                        elif abs(histo_array[i][b]) > yield_thr:
                            res_high +=1
               
                    logging.info('histogramming %r' % mean_array[i]['chip-number'])
                    print 'median of FE %s is : %s with %i vias connected' %(mean_array[i]['chip-number'],np.median(meancalc),count)
                print low_mean
                rel = float(res_low)/float(res_high + res_low)
                
                f.writerow(['high resistance',res_high])
                f.writerow(['low resistance',res_low])
                f.writerow(['yield', rel])

            print 'number of FE\'s : %r' % len(mean_array)
            print 'total number of vias : %i' % (res_low + res_high)
            print 'histogram and data file written to: %r' % file_name
            print 'not connected : %i vias' % res_high, '\nconnected : %i vias' % res_low
            print 'yield = %.3f' % rel
            print 'mean resistance of connected vias = %s' % np.mean(low_mean)
            

            ax.set_title('Yield of vias on %i FE' % size)
            ax.set_xlabel('resistance [Ohm]')
            ax.set_ylabel('number of vias')
            ax.set_xscale('log')
            ax.set_xlim(1e-2,1e9)
            ax.grid()
            spacing = [0.01, 0.1, 1, 10, 100, 1000, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e9] #np.logspace(np.log10(0.01),np.log10(10.0), 10)
            print spacing
            ax.set_xticks(spacing)
#             plt.ylim(0,20)
            mean_values,mean_std_devs = self.unpack_uncertainties(histo_data)
            
            ax.hist(mean_values, bins = spacing)
#             plt.hist(mean_values, bins = 10**np.linspace(np.log10(0.1), np.log(1e5),15),align='mid')
#             plt.hist(mean_values, bins = [1e-1,1, 10, 100, 1000, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11],align='right')#= 10**np.linspace(np.log10(0.1), np.log(1e5),50))
            thr2 = ax.axvline(x=yield_thr, ymin=0, ymax = 200, linewidth=2.5, color = 'crimson', linestyle = '--',label = 'threshold of %r $\Omega$' % yield_thr)
#             plt.hist(mean_values, bins = [0, 0.5, 1,2, 3, 4, 5,6,7,8,9,10])
#             extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
#             ax.legend([extra],('rate of vias < 1 Ohm : \n %.3f' %rel),bbox_to_anchor=(1, 1))
            r = np.round(np.mean(low_mean),2)   
#             box = AnchoredText(' vias $\leq$ 1 $\Omega$: %2.f %% \n mean R : %.2f $\pm 0.01$ $\Omega$' %(rel*100, r), loc=1,fancybox = True)
#             ax.add_artist(box)
            props = dict(boxstyle='round', facecolor='white', alpha=0.2)
            text = ax.text(0.67,0.95, 'yield = %2.0f%%               \nmean R = %.2f $\Omega$ \n\n' % (rel*100,r) ,verticalalignment='top',transform=ax.transAxes,bbox=props)
            ax.legend(handles = [thr2], loc = 'right',bbox_to_anchor=(1,0.82),frameon = False ,framealpha = 1)
            output_pdf.savefig(fig) 
            
        
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")        
    func = TSV_res_meas_analysis()
#     os.chdir('/media/niko/data/TSV-measurements')        

    '''
    Plot all vias
    '''
    dirpath_all = [
                    '/media/niko/data/TSV-measurements/TSV-D7/resmeas-keithley2400',
                    '/media/niko/data/TSV-measurements/TSV-D8/resmeas-keithley2400',
                    '/media/niko/data/TSV-measurements/TSV-D9/resmeas-keithley2400',
                    '/media/niko/data/TSV-measurements/TSV-D10/resmeas-keithley2400',
                    '/media/niko/data/TSV-measurements/TSV-D11/resmeas-keithley2400',
                    '/media/niko/data/TSV-measurements/TSV-D12/resmeas-keithley2400',
                    '/media/niko/data/TSV-measurements/TSV-D13/resmeas-keithley2410',
                    '/media/niko/data/TSV-measurements/TSV-D14/resmeas-keithley2410',
                    '/media/niko/data/TSV-measurements/TSV-D15/resmeas-keithley2410',
                    '/media/niko/data/TSV-measurements/TSV-D16/resmeas-keithley2410',
                    '/media/niko/data/TSV-measurements/TSV-D3/resmeas3_new_sm',
                    '/media/niko/data/TSV-measurements/TSV-D4/resmeas2_new_sm',
                    '/media/niko/data/TSV-measurements/TSV-D5/resmeas2_new_sm',
                    '/media/niko/data/TSV-measurements/TSV-D6/resmeas2_new_sm',
                    '/media/niko/data/TSV-measurements/TSV-S4/resmeas',
                    '/media/niko/data/TSV-measurements/TSV-S5/resmeas',
                    '/media/niko/data/TSV-measurements/TSV-S6/resmeas',
                    '/media/niko/data/TSV-measurements/TSV-S7/resmeas',
                    '/media/niko/data/TSV-measurements/TSV-S8/resmeas',
                    '/media/niko/data/TSV-measurements/TSV-S9/resmeas-keithley2410',
                    '/media/niko/data/TSV-measurements/TSV-S10/resmeas-keithley2410']
    
    f= 'via2-300mamp-4wire.csv'

    p = (0.1,0.5)
    fit=2
    histo = False
    yield_thr = 1
    mean_array = []
    mean_per_fe = []
    print dirpath_all[15]
    x,y,title = func.load_file_no_err(os.path.join(dirpath_all[15], f))
 
#     func.plot_single_via(x, y, z, p, fit=False)
#     func.mean_per_FE(dirpath_all[15],plotmarker = 2)
#     func.plot_IV_curve(x, y, title, logy=False)
#     func.fitfunction_single_via(x, z, p0)   
#     print func.mean_res_1_via(z)
#     func.histo_1_via(z,50,'blue')
    '''
    Array for map/histo of all FE
    ''' 
    for i in xrange(len(dirpath_all)):
        mean = func.mean_per_FE(dirpath_all[i],plotmarker = 3)
        mean_array.append(mean)
        mean_per_fe.append(np.mean(mean['via-means']))
    
#     mean = func.mean_per_FE(dirpath_all[0],plotmarker = 3)             
#     func.histo_FEs(mean_per_fe)
#     func.mean_per_FE(dirpath_all[2], fit)
    func.plot_all_FE(mean_array, 'position', yield_thr, '/media/niko/data/TSV-measurements/testest') # choose either 'numbers' or 'position'
    logging.info('finished')