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

import os
import logging
import path
import re
from numpy.core.defchararray import endswith
from uncertainties.unumpy.core import uarray



class TSV_res_meas_analysis(object):
    
    '''
    Via map gives the horizontal position of every via with respect to the center of the leftmost wirebond pad (#1)
    on the upper side of the FE
    '''
    
    via_map = {'via1':-169, 'via2':59, 'via3':1090, 'via4':1467, 'via5':1390, 'via6':2067, 'via7':2367, 'via8':3575, 'via9':3725, 'via10':5375,
               'via11':5675, 'via12':8675, 'via13':8825, 'via14':8963, 'via15':11800, 'via16':11950, 'via17':14275, 'via18':16312, 'via19':16550,
               'via20':16700, 'via21':17750, 'via22':17900, 'via23':18050, 'via24':18200, 'via25':19336, 'via26':19719} 
    
    
    def __init__(self, outformat='pdf'):
        
        self.outformat=outformat
        self.outfile = ''
        self.error=False
        


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

        return x1, y1, z1

    
    def plot_single_via(self, x, y, z, p0, fit, voltage=True):

        x1,x2 = self.unpack_uncertainties(x)
        y1,y2 = self.unpack_uncertainties(y)
        z1,z2 = self.unpack_uncertainties(z)
        first = 0
        ymax = 1.1*np.amax(z1)
        plt.cla()
        plt.ylim(0,ymax)     
        plt.title(self.title)

        m = np.mean(z)
#         m = np.round(np.mean(z[first:]),4)    # use this line instead the upper one, in case of sm 2410 (first 40 values are rubbish)
        if voltage is True:
            plt.xlabel('Voltage [V]')
            xmax = 1.1*np.amax(x1)
            plt.xlim(0,xmax)
            mpl.rcParams['legend.handlelength'] = 0
#             plt.plot(x1,z1, 'b.', markersize = 3,label=' Data \n mean = %s' %m)
            plt.errorbar(x1, z1, yerr = z2, errorevery = 4, color = 'blue', marker = 'o', markersize = 2,label=' Data \n mean = %s' %m)          
        else :
            plt.xlabel('Current [A]')
            xmax = 1.1*np.amax(y1)
            plt.xlim(0,xmax)
            plt.plot(y1,z1,label='Data  mean = %s' %m, marker = '.', color='blue')
            plt.errorbar(y1, z1,yerr = z2)
        plt.ylabel('Resistance [Ohm]')
        if fit:
            p, _ =  curve_fit(self.fitfunction_line, x[first:], z[first:], p0) 
            plt.plot(self.fitfunction_line(x[first:],*p), 'r',label='Fit')
#             print curve_fit(self.fitfunction_single_via, x, z, p0=(1,-1,10))
            print 'fit succesful: b = %r' % p[1]
            #except: 
             #   logging.error('Fit failed!') 
#         plt.text(0.1,0,'mean = %r' %np.round(np.mean(z[40:]),3))
        plt.legend(loc='best', numpoints = 1)
        plt.grid()
#         box = AnchoredText('mean = %f' %np.round(np.mean(z[first:]),3), loc='right center')
#         ax = plt.axes()
#         ax.add_artist(box)        
        plt.savefig(self.outfile + '.'+ self.outformat)
        plt.show()
    
    
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
        return m*x + b
        
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
    
    def plot_IV_curve(self,x,y):

        voltage, voltage_std_dev = self.unpack_uncertainties(x)
        current, current_std_dev = self.unpack_uncertainties(y)
        
        p, covariance =  curve_fit(self.fitfunction_line, x, y, p0=(0,0))
        plt.cla()
#         plt.xlim(0,0.2)
#         plt.ylim(0,0.3)
        plt.title(self.title + ' IV curve')
        plt.ylabel('Current [A]')
        plt.xlabel('Voltage [V]')
#         plt.errorbar(x, y, yerr=e, fmt=None)
#         box = AnchoredText('m = %.3f \n b = %.5f' %(p[0],p[1]), bbox_to_anchor=(1,1),loc=1)
        textstr=('m = %.3f \n b = %.5f' %(p[0],p[1]))
        ax = plt.axes()
#         ax.text(0.1, round(((ax.get_ylim()[1] + ax.get_ylim()[0])/2), 0), textstr, bbox=dict(boxstyle='square', facecolor='white'))
#         ax.add_artist(box)
        plt.errorbar(voltage,current, voltage_std_dev, current_std_dev, 'b.', markersize = 3, label = 'data')
        plt.plot(voltage, self.fitfunction_line(x, *p),'r-', linewidth = 1.2, label = 'fit \n'+ textstr)
        leg = plt.legend(loc = 'best', numpoints = 1)
#         plt.draw()
#         loc = leg.get_window_extent().inverse_transformed(ax.transAxes)
#         loc = leg.get_frame().get_bbox().bounds
#         print loc
#         leg_height = loc.p1[1]-loc.p1[0]
#         print leg_height
#         textbox = ax.text(-loc.p0[0]-0.05,-loc.p0[1]-0.05, textstr, bbox=dict(boxstyle='square', facecolor='white'))
        print 'covariance: %r' % (np.sqrt(np.diag(covariance)))
        print 'fit: %r' % p
        
        plt.savefig(self.outfile + '-IV-fit.'+ self.outformat)
        plt.show()
     
    def unpack_uncertainties (self, x):
    
        nominal,std_dev = [],[]

        for i in xrange(len(x)):
            nominal.append(unc.nominal_value(x[i]))
            std_dev.append(unc.std_dev(x[i]))
        
        return nominal,std_dev
        
    def mean_per_FE(self,path, plotmarker):
                
        means, files, number = [],[],[]
        via = 1
        for file in os.listdir(path):
            if file.endswith('.csv'):
#                 files.append(split.file('via','-')[1])
                files.append(os.path.split(file)[1]) #.split('via','-')[1]  
        logging.info('%r vias found, processing ...' %len(files))
        os.chdir(path)
        chip_number = os.path.split(os.path.split(path)[0])[1]

        for i in xrange(len(files)):
            number.append(int(re.split('(\d+)',files[i])[1]))
            means.append(np.mean(self.load_file('via' + str(number[-1]) + '-300mamp-4wire.csv')[2])) #[50:]
            
        means1,means2 = self.unpack_uncertainties(means)
        
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
            plt.errorbar(x, means1, yerr=yerr, ls = 'None', marker = 'o', markersize = 3,color = 'blue',label = 'mean per via')  
            plt.legend(loc = 'best', numpoints=1)
            plt.savefig(chip_number + '-distribution-map-scatter.pdf')
        
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
#             plt.plot(x,y_nom, 'b.', markersize = 1, label = 'mean per via')
            plt.errorbar(x, y_nom, yerr=yerr, ls = 'None',marker = 'o', markersize = 3,color = 'blue',label = 'mean per via')

            plt.title('Local distribution of vias on ' + chip_number)
            plt.xlabel('position [mm]')
            plt.ylabel('Resistance [Ohm]')
            plt.grid()
            plt.xlim(-0.5,20.1)
            plt.gca().set_yscale('log')
            plt.legend(loc = 'best', numpoints=1)
#             plt.show()
            plt.savefig(chip_number + '-map-mm.pdf')            
        
        elif plotmarker==3:
            loc = {}
            x,y = [],[]
            for i in xrange (len(number)):
                loc.update({float(TSV_res_meas_analysis.via_map['via' + str(number[i])])/1000 : means[i]})
            for i in xrange (len(loc)):
                x = loc.keys()
                y = loc.values()
            means = y
            logging.info('calculating means only')
        
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
        
        plt.plot(number, mean1[1], 'b.', label = mean1[2], markersize = 8)
        plt.plot(number, mean2[1], 'r.', label = mean2[2], markersize = 8)
        plt.plot(number, mean3[1],'g.' , label = mean3[2], markersize = 8)
        
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
     
    def plot_all_FE (self, mean_array, histo, x_unit, yield_thr, destination):
        
        size = len(mean_array)
        os.chdir(destination)
        file_name = destination + '/histogram-data-of-' + str(size) + '-FE-unc.csv'
        count = 0
        meancalc = []
        
        if not histo:    
            plt.cla()
            plt.title('Local distribution of via resistance on %i FE' % size )

            plt.ylabel('Resistance [Ohm]')
            plt.grid()
            plt.gca().set_yscale('log')
            plt.ylim(1e-2,1e10)
            means1,means2 = [],[]
                
            for i in xrange (len(mean_array)):
                means1,means2 = self.unpack_uncertainties(mean_array[i]['via-means'])
                count  = 0
                for i in means1:
                    if means1[i] < 1:
                        count += 1
                        meancalc.append(means1[i])
#                 plt.plot(mean_array[i]['via-'+ x_unit], means1, '.', label = str(mean_array[i]['chip-number']), markersize = 8)
                plt.errorbar(mean_array[i]['via-'+ x_unit], means1, means2, marker = 'o',ls = 'None', label = str(mean_array[i]['chip-number']), markersize = 4)
                
                logging.info('plotting for FE %r' % mean_array[i]['chip-number'])
                print 'mean of FE %s is: %s with %i vias connected' %(mean_array[i]['chip-number'],np.mean(meancalc),count)
            
            if x_unit == 'position':
                plt.xlim(-0.5,20.5)
                plt.xlabel('via postion [mm]')
            elif x_unit =='numbers':
                plt.xlim(0,27)  
                plt.xlabel('via index') 
                labels = map(int, sorted(mean_array[i]['via-numbers'],key = int))
                plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
#             box = plt.subplot(111).get_position()
#             plt.subplot(111).set_position([box.x0, box.y0, box.width * 0.8, box.height])
            lgd = plt.subplot(111).legend(loc = 'center right', bbox_to_anchor=(0.98, 0.8,0.23,0.1), numpoints = 1, borderaxespad=0)#, mode = 'expand'
#             plt.legend(loc = 'best', numpoints=1)
            if x_unit == 'position':
                plt.savefig('map-for-' + str(size)+ '-FE-mm-test.pdf', bbox_inches='tight') #bbox_extra_artists=(lgd),
            elif x_unit == 'numbers':
                plt.savefig('map-for-' + str(size)+ '-FE-test.pdf', bbox_inches='tight')
            plt.show()
                
        if histo:        
            histo_array,histo_data, mean_values,mean_std_devs, low_mean,res_high, res_low = [], [], [],[],[], 0, 0
                    
            with open(file_name, 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                f.writerow(['Resistance [ohm]']) 
 
                for i in xrange(len(mean_array)):
                    histo_array.append(mean_array[i]['via-means'])
                    count = 0
                    for b in xrange(len(histo_array[i])): 
                        histo_data.append(histo_array[i][b])
                        if histo_data[-1] <=1:
                            meancalc.append(histo_data[-1])
                            count +=1
#                         print histo_data[-1], type(histo_data[-1])
                        f.writerow([unc.nominal_value(histo_data[-1]),unc.std_dev(histo_data[-1])])
                        if histo_array[i][b] <= yield_thr :
                            low_mean.append(histo_array[i][b])
                            res_low += 1
                        elif histo_array[i][b] > yield_thr:
                            res_high +=1
                    logging.info('histogramming %r' % mean_array[i]['chip-number'])
                    print 'mean of FE %s is : %s with %i vias connected' %(mean_array[i]['chip-number'],np.mean(meancalc),count)
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
            
            plt.cla()
            plt.title('Yield of vias on %i FE' % size)
            plt.xlabel('resistance [Ohm]')
            plt.ylabel('number of vias')
            plt.gca().set_xscale('log')
#             plt.xlim(1e-2,1e11)
#             plt.ylim(0,20)
            mean_values,mean_std_devs = self.unpack_uncertainties(histo_data)
            plt.hist(mean_values, bins = [1e-2, 1e-1,1, 10, 100, 1000, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11])#= 10**np.linspace(np.log10(0.1), np.log(1e5),50))
#             plt.hist(mean_values, bins = [0, 0.5, 1,2, 3, 4, 5,6,7,8,9,10])
#             extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
#             plt.legend([extra],('rate of vias < 1 Ohm : \n %.3f' %rel),bbox_to_anchor=(1, 1))
            r = unc.nominal_value(np.mean(low_mean))
            r2 = ufloat(r, 0.013)            
            box = AnchoredText(' vias <= 1 Ohm : %.1f %% \n mean R : %s Ohm' %(rel*100, r2), loc=1)
            ax = plt.axes()
            ax.add_artist(box)
            
            plt.savefig('histogram-of-' + str(size) + 'FE-with-mean-and-uncertainties.pdf')
            plt.show()
            
        
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")        
    func = TSV_res_meas_analysis()
#     os.chdir('/media/niko/data/TSV-measurements')        
    '''
    Plot single via
    '''
    dirpath = '/media/niko/data/TSV-measurements/TSV-D3/resmeas3_new_sm'
    '''
    Plot all vias
    '''
    dirpath_all = ['/media/niko/data/TSV-measurements/TSV-D3/resmeas3_new_sm',
                   '/media/niko/data/TSV-measurements/TSV-D4/resmeas2_new_sm',
                   '/media/niko/data/TSV-measurements/TSV-D5/resmeas2_new_sm',
                   '/media/niko/data/TSV-measurements/TSV-D6/resmeas2_new_sm',
                   '/media/niko/data/TSV-measurements/TSV-S4/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-S5/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-S6/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-S7/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-S8/resmeas']
    
    f= 'via8-300mamp-4wire.csv'

    p = (0.1,0.5)
    fit=3
    histo = True
    yield_thr = 1
    mean_array = []
    
    x,y,z = func.load_file(os.path.join(dirpath, f))
 
#     func.plot_single_via(x, y, z, p, fit=False)
#     func.fitfunction_single_via(x, z, p0)   
#     print func.mean_res_1_via(z)
#     func.histo_1_via(z,50,'blue')
    '''
    Array for map/histo of all FE
    ''' 
    for i in xrange(len(dirpath_all)):
        mean_array.append(func.mean_per_FE(dirpath_all[i],fit))
#         mean_per_fe.append(np.mean(func.mean_per_FE(dirpath_all[i],fit)['via-means']))
    
                  
#     func.histo_FEs(mean_per_fe)
#     func.mean_per_FE(dirpath_all[3], fit)
    func.plot_all_FE(mean_array, histo, 'position', yield_thr, '/media/niko/data/TSV-measurements') # choose either 'numbers' or 'position'
    logging.info('finished')