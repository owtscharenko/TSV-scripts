import matplotlib.pyplot as plt
import numpy as np
import csv
from decimal import Decimal as dec

import os
import logging
import path


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
    
    def plot_single_via(self,x,y,z,voltage=True):

        ymax = 1.1*np.amax(z)
        
        plt.cla()
        plt.ylim(0,ymax)     
        plt.title(self.title)
        
#         for i in range (0,len(z)):
#             print x[i]
        if voltage is True:
            plt.xlabel('Voltage [mV]')
            xmax = 1.1*np.amax(x)
            plt.xlim(-0.1*xmax,xmax)
            plt.plot(x,z, 'b.', markersize = 3,label='Data')
              
        else :
            plt.xlabel('Current [mA]')
            xmax = 1.1*np.amax(y)
            plt.xlim(-0.1*xmax,xmax)
            plt.plot(y,z,label='Data',marker = '.', color='blue')
        plt.ylabel('Resistance [Ohm]')
        
        plt.grid()
        plt.savefig(self.outfile + '.'+ self.outformat)
#         plt.show()
        
    
    
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
        
    
    
    
if __name__ == "__main__":
        
    func = TSV_res_meas_analysis()
        
    '''
    Plot single via
    '''
    dirpath = '/media/niko/data/Niko/test_sm'
    f= 'via99-50mvolt-2wire_8.csv'
        
    x,y,z = func.load_file(os.path.join(dirpath, f))
   
#     func.plot_single_via(x, y, z)     
#     print func.mean_res_1_via(z)
    func.histo_1_via(z,50,'blue')
    logging.info('finished')