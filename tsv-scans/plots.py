import matplotlib.pyplot as plt
import numpy as np
import csv
from decimal import Decimal as dec
from scipy.optimize import curve_fit

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



    def wirebond_corr(self, data, length_t, length_b, spec_res):
        r_via_top = length_t*spec_res
        r_via_bottom = length_b*spec_res
        total_r = r_via_bottom + r_via_top
        data_corr = np.subtract(data,total_r)    
        return data_corr





    def fitfunction_gauss(self,x,*p):
        A,mu,sigma = p 
        return A*np.exp(-(x-mu)**2/(2*sigma**2))
    
    def plot_single_via(self, x, y, z, p0, fit, voltage=True):
        
        first = 0
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
            plt.plot(x,z, 'b.', markersize = 3,label='Data \n mean = %.4f' %m)              
        else :
            plt.xlabel('Current [A]')
            xmax = 1.1*np.amax(y)
            plt.xlim(0,xmax)
            plt.plot(y,z,label='Data \n mean = %.4f' %m, marker = '.', color='blue')
        plt.ylabel('Resistance [Ohm]')
        if fit:
            p, _ =  curve_fit(self.fitfunction_exp, x[50:], z[50:], p0) 
            plt.plot(self.fitfunction_exp(x[50:],*p), 'r',label='Fit')
#             print curve_fit(self.fitfunction_single_via, x, z, p0=(1,-1,10))
            print p # fit succesful, %r,%r,%r,%r,%r' % p
            #except: 
             #   logging.error('Fit failed!') 
        plt.legend(loc='lower right')
        plt.grid()
        plt.savefig(self.outfile + '.'+ self.outformat)
#         plt.show()
    
    
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
#         plt.text(x, y, str(np.mean(z[40:])))
        plt.grid()
        plt.savefig(self.outfile + '-zoom' + '.'+ self.outformat)
#         plt.show()    
    
    
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
        
    
    
    
if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")
    
    func = TSV_res_meas_analysis()        
    '''
    Plot single via
    '''
    dirpath = '/media/niko/data/Niko/TSV-D4/resmeas'
    f= 'via7-300mamp-4wire.csv'
    
#     p = (1, 10, 10,10,10000,1000000)    # polynom
    p=(0.05,-2,0.5)  # exp    
    fit=False
    x,y,z = func.load_file(os.path.join(dirpath, f))
   
    func.plot_single_via(x, y, z, p, fit)
#     func.fitfunction_single_via(x, z, p0)   
#     print func.mean_res_1_via(z)
#     func.histo_1_via(z,50,'blue')
    logging.info('finished')