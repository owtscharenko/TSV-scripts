import matplotlib.pyplot as plt
import numpy as np
import csv
from decimal import Decimal as dec
from scipy.optimize import curve_fit
from matplotlib.offsetbox import AnchoredText

import os
import logging
import path
import re
from numpy.core.defchararray import endswith



class TSV_res_meas_analysis(object):


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
            _ = linereader.next()  # Use header to extract multi automatically?
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
        
    def mean_per_FE(self,path, plotmarker):
        
        means, files, number = [],[],[]
        via = 1
        for file in os.listdir(path):
            if file.endswith('.csv'):
#                 files.append(split.file('via','-')[1])
                files.append(os.path.split(file)[1])#.split('via','-')[1]  
        
        logging.info('%r vias found, processing ...' %len(files))
        os.chdir(path)
        chip_number = os.path.split(os.path.split(path)[0])[1]
                         
        for i in range(0, len(files)):
            number.append(int(re.split('(\d+)',files[i])[1]))
            means.append(np.mean(self.load_file('via' + str(number[-1]) + '-300mamp-4wire.csv')[2])) #[50:]
#         print number
        
        if plotmarker:
            plt.cla()
            plt.title('vias on ' + chip_number)
            plt.grid()
            #plt.xlim(0,10**np.log(1e3))
            plt.hist(means, bins = 10**np.linspace(np.log10(0.1), np.log(1e5),18)) #logarithmic binning 
            logging.debug('wtf')
            plt.gca().set_xscale('log')
            plt.xlabel('Mean resistance in Ohm')
            plt.ylabel('Count')
            plt.savefig(chip_number + '-resistance-histogram.pdf') 
            
            '''Plotting "map" '''
            
            plt.cla()
            plt.title('Local distribution of vias on ' + chip_number)
            plt.xlabel('Number of via')
            plt.ylabel('Resistance in Ohm')
            plt.grid()
            plt.xlim(0,27)
            plt.gca().set_yscale('log')
            labels = map(int, sorted(number,key = int))
            plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
    
            plt.plot(number, means, ' b.', markersize = 8, label = 'mean per via')
        
            plt.legend(loc = 'best', numpoints=1)
            plt.savefig(chip_number + '-distribution-map.pdf')
        
        else:
            logging.info('calculating means only')
        
        return {'via-numbers' : number, 'via-means' : means, 'chip-number' : chip_number}   #numbers.append(re.split('(\d+)',files[i])[1])
                
    def plot_3_FE(self, mean1,mean2,mean3):   
    
        chip_numbers = [mean1[2], mean2[2], mean3[2] ]
        number = mean1[0]
        plt.cla()
        plt.title('Local distribution of via resistance on 3 FE ' )#+ mean1[2]  + ' , ' +  mean2[2] + ' and ' + mean3[2])
        plt.xlabel('Number of via')
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
     
     
    def plot_all_FE (self, mean_array,destination):
        
        size = len(mean_array)
        plt.cla()
        plt.title('Local distribution of via resistance on %i FE ' % size )
        plt.xlabel('Number of via')
        plt.ylabel('Resistance in Ohm')
        plt.grid()
        plt.xlim(0,27)
        plt.gca().set_yscale('log')
        
        for i in range(0,len(mean_array)):
#             print mean_array[i][0]
            plt.plot(mean_array[i]['via-numbers'], mean_array[i]['via-means'], '.', label = str(mean_array[i]['chip-number']), markersize = 8)
            logging.info('plotting for FE %r' % mean_array[i]['chip-number'])
            
        labels = map(int, sorted(mean_array[i]['via-numbers'],key = int))
        plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0)) 
        plt.subplot(111).legend(bbox_to_anchor=(1.1, 1.1), numpoints = 1)
        #plt.legend(loc = 'best', numpoints=1)
        os.chdir(destination)
        plt.savefig('distribution-map-for-' + str(size)+ '-FE.pdf')
        plt.show()
        
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")        
    func = TSV_res_meas_analysis()
#     os.chdir('/media/niko/data/TSV-measurements')
        
    '''
    Plot single via
    '''
    dirpath = '/media/niko/data/TSV-measurements/TSV-D3/resmeas3_new_sm'
    
    dirpath_all = ['/media/niko/data/TSV-measurements/TSV-D3/resmeas3_new_sm',
                   '/media/niko/data/TSV-measurements/TSV-D4/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-D5/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-S4/resmeas',
                   '/media/niko/data/TSV-measurements/TSV-S5/resmeas']
    
    f= 'via7-300mamp-4wire.csv'
   
#     p = (1, 10, 10,10,10000,1000000)    # polynom
#     p=(0.05,-2,0.5)  # exp    
    p = (0.1,0.5)
    fit=False
   # x,y,z = func.load_file(os.path.join(dirpath, f))
 
#     func.plot_single_via(x, y, z, p, fit)
#     func.fitfunction_single_via(x, z, p0)   
#     print func.mean_res_1_via(z)
#     func.histo_1_via(z,50,'blue')

#     func.plot_3_FE(func.mean_per_FE(dirpath_all[0],fit), func.mean_per_FE(dirpath_all[1],fit), func.mean_per_FE(dirpath_all[2],fit))
#     print dirpath_all
    mean_array = [func.mean_per_FE(dirpath_all[0],fit),
                  func.mean_per_FE(dirpath_all[1],fit),
                  func.mean_per_FE(dirpath_all[2],fit),
                  func.mean_per_FE(dirpath_all[3],fit),
                  func.mean_per_FE(dirpath_all[4],fit)]
    
    func.plot_all_FE(mean_array,'/media/niko/data/TSV-measurements')
    logging.info('finished')