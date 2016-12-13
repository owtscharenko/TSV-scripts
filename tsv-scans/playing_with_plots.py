import matplotlib.pyplot as plt
import numpy as np
import csv
from decimal import Decimal as dec
from scipy.optimize import curve_fit
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import Rectangle

import os
import logging
import path
import re
from numpy.core.defchararray import endswith



class TSV_res_meas_analysis(object):
    
    '''the via map gives the horizontal position of every via wrt the center of the leftmost wirebond pad on the upper side of the FE'''
    
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
            
        
        x,y,z = [], [], []
        with open(path, 'rb') as datafile:
            linereader = csv.reader(datafile, delimiter=',', quotechar='"')
            _ = linereader.next()
            frow = linereader.next()
        
            x.append(float(frow[0]))
            y.append(float(frow[1]))
            z.append(float(frow[2]))    
            for row in linereader:
                x.append(float(row[0]))
                y.append(float(row[1]))
                z.append(float(row[2]))
                
        return np.round(np.array(x),5), np.round(np.array(y),5), np.round(np.array(z),5)

    def fitfunction_gauss(self,x,*p):
        A,mu,sigma = p 
        return A*np.exp(-(x-mu)**2/(2*sigma**2))
    
    def plot_single_via(self, x, y, z, p0, fit, voltage=True):
        
        first = 40
        ymax = 1.1*np.amax(z)       
        plt.cla()
        plt.ylim(0,ymax)     
        plt.title(self.title)
        m = np.round(np.mean(z),4)
#         m = np.round(np.mean(z[first:]),4)    # use this line instead the upper one, in case of sm 2410 (first 40 values are rubbish)
        if voltage is True:
            plt.xlabel('Voltage [V]')
            xmax = 1.1*np.amax(x)
            plt.xlim(0,xmax)
            plt.plot(x,z, 'b.', markersize = 3,label=' Data \n mean = %.4f' %m)             
        else :
            plt.xlabel('Current [A]')
            xmax = 1.1*np.amax(y)
            plt.xlim(0,xmax)
            plt.plot(y,z,label='Data  mean = %.4f' %m, marker = '.', color='blue')
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

    
    def mean_res_1_via(self,z):
        b = 0
        x = 0
        float(x)
        for i in range(0,len(z)):
            if z[i]>0:
                x=x+z[i]
                b += 1
        return np.round(x/b,5)
    
    
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
    
    
    def plot_IV_curve(self,x,y):

        p, covariance =  curve_fit(self.fitfunction_line, x, y, p0=(0,0))
        plt.cla()
        plt.xlim(0,0.2)
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
        plt.plot(x,y, label = 'data')
        plt.plot(x, self.fitfunction_line(x, *p),'r-', label = 'fit \n'+ textstr)
        leg = plt.legend(loc = 'best')
#         plt.draw()
#         loc = leg.get_window_extent().inverse_transformed(ax.transAxes)
#         loc = leg.get_frame().get_bbox().bounds
#         print loc
#         leg_height = loc.p1[1]-loc.p1[0]
#         print leg_height
#         textbox = ax.text(-loc.p0[0]-0.05,-loc.p0[1]-0.05, textstr, bbox=dict(boxstyle='square', facecolor='white'))
        print 'covariance: %r' % (np.sqrt(np.diag(covariance)))
        print 'fit: %r' % p
        
        plt.savefig('/media/niko/data/TSV-measurements/TSV-S8/resmeas/via6-IV-line-fit.pdf')
        plt.show()
    
        
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

        for i in range(0, len(files)):
            number.append(int(re.split('(\d+)',files[i])[1]))
            means.append(np.mean(self.load_file('via' + str(number[-1]) + '-300mamp-4wire.csv')[2])) #[50:]
            
        
        if plotmarker==1:
            plt.cla()
            plt.title('vias on ' + chip_number)
            plt.grid()
            #plt.xlim(0,10**np.log(1e3))
            plt.hist(means, bins = 10**np.linspace(np.log10(0.1), np.log(1e5),18)) #logarithmic binning 
            
            plt.gca().set_xscale('log')
            plt.xlabel('Mean resistance in Ohm')
            plt.ylabel('Count')
            plt.savefig(chip_number + '-resistance-histogram.pdf') 
            
            '''Plotting "map" '''
            
            plt.cla()
            plt.title('Local distribution of vias on ' + chip_number)
            plt.xlabel('Via index')
            plt.ylabel('Resistance in Ohm')
            plt.grid()
            plt.xlim(0,27)
            plt.gca().set_yscale('log')
            labels = map(int, sorted(number,key = int))
            plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
    
            plt.plot(number, means, ' b.', markersize = 8, label = 'mean per via')
        
            plt.legend(loc = 'best', numpoints=1)
            plt.savefig(chip_number + '-distribution-map-scatter.pdf')
        
        elif plotmarker==2:
            '''Plotting real map (location of via in mm relative to lower left corner/ Pad 1) '''
            
            loc = {}
            x,y = [],[]
            plt.cla()
            for i in xrange (len(number)):
                loc.update({float(TSV_res_meas_analysis.via_map['via' + str(number[i])])/1000 : means[i]})
            for i in xrange (len(loc)):
                x = loc.keys()
                y = loc.values()
            plt.plot(x,y, 'b.', markersize = 7, label = 'mean per via')

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
        file_name = destination + '/histogram-data-of-' + str(size) + '-FE.csv'
        
        if not histo:    
            plt.cla()
            plt.title('Local distribution of via resistance on %i FE' % size )

            plt.ylabel('Resistance [Ohm]')
            plt.grid()
            plt.gca().set_yscale('log')
            plt.ylim(1e-2,1e10)
                
            for i in xrange (len(mean_array)):
                plt.plot(mean_array[i]['via-'+ x_unit], mean_array[i]['via-means'], '.', label = str(mean_array[i]['chip-number']), markersize = 8)
                logging.info('plotting for FE %r' % mean_array[i]['chip-number'])
            
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
                plt.savefig('map-for-' + str(size)+ '-FE-mm.pdf', bbox_inches='tight') #bbox_extra_artists=(lgd),
            elif x_unit == 'numbers':
                plt.savefig('map-for-' + str(size)+ '-FE.pdf', bbox_inches='tight')
            plt.show()
                
        if histo:
            
            histo_array,histo_data, low_mean,res_high, res_low = [], [], [], 0, 0
            
            with open(file_name, 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                f.writerow(['Resistance [ohm]'])
                for i in xrange(len(mean_array)):
                    histo_array.append(mean_array[i]['via-means'])
                    for b in xrange(len(histo_array[i])):
                        histo_data.append(histo_array[i][b])
#                         print histo_data[-1], type(histo_data[-1])
                        f.writerow([histo_data[-1]])
                        if histo_array[i][b] <= yield_thr :
                            low_mean.append(histo_array[i][b])
                            res_low += 1
                        elif histo_array[i][b] > yield_thr:
                            res_high +=1
                    logging.info('histogramming %r' % mean_array[i]['chip-number'])
                rel = float(res_low)/float(res_high + res_low)
                
                f.writerow(['high resistance',res_high])
                f.writerow(['low resistance',res_low])
                f.writerow(['yield', rel])

            print 'number of FE = %r' % len(histo_array)
            print 'total number of vias = %r' % len(histo_data)
            print 'histogram and data file written to: %r' % file_name
            print 'res_high = %i' % res_high, 'res_low = %i' % res_low
            print 'yield = %.3f' % rel
            print 'mean resistance of connected vias = %.3f' % np.mean(low_mean)
            
            plt.cla()
            plt.title('Yield of vias on %i FE' % size)
            plt.xlabel('resistance [Ohm]')
            plt.ylabel('number of vias')
            plt.gca().set_xscale('log')
            plt.xlim(1e-2,1e11)
#             plt.ylim(0,20)
            plt.hist(histo_data, bins = [1e-2, 1e-1,0.2,0.5, 1, 10, 100, 1000, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11])#= 10**np.linspace(np.log10(0.1), np.log(1e5),50))
#             extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
#             plt.legend([extra],('rate of vias < 1 Ohm : \n %.3f' %rel),bbox_to_anchor=(1, 1))
            box = AnchoredText('vias < 1 Ohm : %.1f %% \n mean res : %.3f Ohm' %(rel*100, np.mean(low_mean)), loc=1)
            ax = plt.axes()
            ax.add_artist(box)
            
            plt.savefig('histogram-of-' + str(size) + 'FE-with-mean.pdf')
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
    
    f= 'via7-300mamp-4wire.csv'

    p = (0.1,0.5)
    fit=2
    histo = True
    yield_thr = 1
    mean_array = []
#     x,y,z = func.load_file(os.path.join(dirpath, f))
 
#     func.plot_single_via(x, y, z, p, fit)
#     func.fitfunction_single_via(x, z, p0)   
#     print func.mean_res_1_via(z)
#     func.histo_1_via(z,50,'blue')
#     func.plot_3_FE(func.mean_per_FE(dirpath_all[0],fit), func.mean_per_FE(dirpath_all[1],fit), func.mean_per_FE(dirpath_all[2],fit))
    '''
    Array for map/histo of all FE
    ''' 
    for i in xrange(len(dirpath_all)):
        mean_array.append(func.mean_per_FE(dirpath_all[i],fit))
                  
    
#     func.mean_per_FE(dirpath_all[3], fit)
    func.plot_all_FE(mean_array, histo, 'position', yield_thr, '/media/niko/data/TSV-measurements') # choose either 'numbers' ord 'position'
    logging.info('finished')