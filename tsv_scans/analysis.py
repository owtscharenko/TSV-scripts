import matplotlib.pyplot as plt
import matplotlib as mpl
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




'''
class for analysis of resistance and LCR-meter data of FE-I4 with TSV
'''

class TSV_analysis(object):

    '''
    This via map gives the horizontal position of every via with respect to the center of the leftmost wirebond pad (#1)
    on the top of FE-I4B
    '''
    
    via_map = {'via1':-169, 'via2':59, 'via3':1090, 'via4':1467, 'via5':1390, 'via6':2067, 'via7':2367, 'via8':3575, 'via9':3725, 'via10':5375,
               'via11':5675, 'via12':8675, 'via13':8825, 'via14':8963, 'via15':11800, 'via16':11950, 'via17':14275, 'via18':16312, 'via19':16550,
               'via20':16700, 'via21':17750, 'via22':17900, 'via23':18050, 'via24':18200, 'via25':19336, 'via26':19719} 

 
    def fitfunction_line (self, x, *p):
        m,b = p
        return m*x+b


    def plot_IV_curve(self, datafile, logy):
        
        '''plotting IV curve from .csv datafile
           file is saved in workdir, path is logged
        '''
        
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

        if not logy:
            file_name = 'fit'  
            plt.plot(voltage, current, '.', markersize = 5, label = 'data' )
            plt.plot(voltage, self.fitfunction_line(voltage, *p),'-', linewidth = 2, label = 'fit\n' + textstr)
            print 'covariance: %r' % (np.sqrt(np.diag(covariance)))
            print 'fit: %r' % p
        if logy:
            file_name = 'plot-log'
            plt.semilogy(voltage,current, label = 'data')
        plt.legend(loc = 'best')
        plt.savefig(datafile[:-4] + '-IV-' + file_name + '.pdf')
        logging.info('IV-plot saved to %s' % (datafile[:-4] + '-IV-' + file_name + '.pdf'))


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
        
    
    
    def plot_FE(self, folder, resistance_array, plotmarker=2):
        
        '''create folder and plot title'''
        if not os.path.exists(folder + '/new-plots'):
            os.makedirs(folder + '/new-plots')
        savedir = folder + '/new-plots/'
        path_list = folder.split(os.sep)
        
        res = resistance_array[:,0]
        
        err = resistance_array[:,1]
        via_number = resistance_array[:,2].tolist()

        chip = path_list[5]

        if plotmarker==1:
            '''plotting histo and map''' 
            
            plt.cla()
            plt.title('vias on ' + chip)
            plt.grid()
#             histo, bins = np.histogram(res,bins = 10**np.linspace(np.log10(0.1), np.log(1e5),18))
#             center = (bins[:-1] + bins[1:]) / 2
#             plt.bar(center, histo) #logarithmic binning 
            plt.hist(res, bins = 10**np.linspace(np.log10(0.1), np.log(1e5),18))
            plt.gca().set_xscale('log')
            plt.xlabel('Mean resistance in Ohm')
            plt.ylabel('Count')
            plt.savefig(savedir + chip + '-resistance-histogram.pdf') 

            '''Plotting "map" (via index on x-axis) '''
            
            plt.cla()
            plt.title('Local distribution of vias on ' + chip)
            plt.xlabel('Via index')
            plt.ylabel('Resistance in Ohm')
            plt.grid()
            plt.xlim(0,27)
            plt.gca().set_yscale('log')
            labels = map(int, sorted(via_number,key = int))
            plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
#             plt.plot(number, means1, ' b.', markersize = 8, label = 'mean per via')
            plt.errorbar(via_number, res, yerr=err, ls = 'None', marker = 'o', markersize = 3,label = 'mean per via')  
            plt.legend(loc = 'best', numpoints=1)
            plt.savefig(savedir + chip + '-distribution-map-scatter.pdf')

        
        elif plotmarker==2:
            '''Plotting only real map (location of via in mm relative to lower left corner/ Pad 1) '''
            
            loc = {}
            x,y = [],[]
            for i in xrange (len(via_number)):
                loc.update({float(TSV_analysis.via_map['via' + str(int(via_number[i]))])/1000 : res[i]})
            for i in xrange (len(loc)):
                x = loc.keys()
                y = loc.values()
#             y_nom, yerr = self.unpack_uncertainties(y)

            plt.cla()    
            plt.plot(x,y, 'o', markersize = 3, label = 'mean resistance per via')
#             plt.errorbar(x, y_nom, yerr=yerr, ls = 'None',marker = 'o', markersize = 3,label = 'mean resistance per via')

            plt.title('Local distribution of vias on ' + chip)
            plt.xlabel('Position on chip [mm]')
            plt.ylabel('Resistance [Ohm]')
            plt.grid()
            plt.xlim(-0.5,20.1)
            plt.gca().set_yscale('log')
            plt.legend(loc = 'best', numpoints=1)

            plt.savefig(savedir + chip + '-map-mm.pdf')     
                   
        logging.info('plotting of %r finished' % chip)    
                
    
    
    def plot_all_FE (self, mean_array, x_unit, yield_thr, destination,histo):
        
        size = len(mean_array)
        os.chdir(destination)
        file_name = destination + '/histogram-data-of-' + str(size) + '-FE-unc.csv'
        count = 0
        meancalc = []
        
        plt.clf()
        
        if not histo:    
            plt.title('Local distribution of via resistance on %i FE' % size )
            plt.ylabel('Resistance [Ohm]')
            plt.grid()
            plt.gca().set_yscale('log')
            plt.ylim(1e-2,1e10)
            means1,means2 = [],[]
            high = 0
            rel = 0
            total_count= 0
                            
            for i in xrange (len(mean_array)):
                means1,means2 = self.unpack_uncertainties(mean_array[i]['via-means'])
                count = 0
                for t in xrange (len(means1)):
                    if means1[t] <= 1:
                        count += 1
                        meancalc.append(means1[i])
                    else:
                        high +=1
                plt.plot(mean_array[i]['via-'+ x_unit], means1, '.', label = str(mean_array[i]['chip-number']), markersize = 8)
                plt.errorbar(mean_array[i]['via-'+ x_unit], means1, means2, marker = 'o',ls = 'None', label = str(mean_array[i]['chip-number']), markersize = 4)
                
                
                logging.info('plotting for FE %r' % mean_array[i]['chip-number'])
                print 'mean of FE %s is: %s with %i vias connected' %(mean_array[i]['chip-number'],np.mean(meancalc),count)
                total_count += count
                  
            if x_unit == 'position':
                plt.xlim(-0.5,20.5)
                plt.xlabel('Postion on chip [mm]')
            elif x_unit =='numbers':
                plt.xlim(0,27)  
                plt.xlabel('via index') 
                labels = map(int, sorted(mean_array[i]['via-numbers'],key = int))
                plt.xticks( np.arange(min(labels)-1, max(labels)+2, 2.0))
                
            rel = float(total_count)/float(total_count + high)# computing yield
            
#             plt.subplot(111).legend(loc = 'upper right', bbox_to_anchor=(0.98, 0.8,0.19,0.19), numpoints = 1, borderaxespad=0)#, mode = 'expand'
            props = dict(boxstyle='square', facecolor='wheat', alpha=0.5)
            plt.subplot(111).text(0.98, 0.77, 'connected: %i \nyield: %2.0f %%' % (total_count,rel*100),verticalalignment='top',transform=plt.subplot(111).transAxes,bbox=props)
            if x_unit == 'position':
                plt.savefig('map-for-' + str(size)+ '-FE-mm-new-stash2.pdf', bbox_inches='tight') #bbox_extra_artists=(lgd),
            elif x_unit == 'numbers':
                plt.savefig('map-for-' + str(size)+ '-FE-new-stash.pdf', bbox_inches='tight')
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
            
            plt.clf()
            plt.title('Yield of vias on %i FE' % size)
            plt.xlabel('resistance [Ohm]')
            plt.ylabel('number of vias')
            plt.gca().set_xscale('log')
            plt.xlim(1e-2,1e9)
            spacing = [0.01, 0.1, 1, 10, 100, 1000, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e9] #np.logspace(np.log10(0.01),np.log10(10.0), 10)
            print spacing
            plt.xticks(spacing)
#             plt.ylim(0,20)
            mean_values,mean_std_devs = self.unpack_uncertainties(histo_data)
            
            plt.hist(mean_values, bins = spacing)
#             plt.hist(mean_values, bins = 10**np.linspace(np.log10(0.1), np.log(1e5),15),align='mid')
#             plt.hist(mean_values, bins = [1e-1,1, 10, 100, 1000, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11],align='right')#= 10**np.linspace(np.log10(0.1), np.log(1e5),50))
            plt.axvline(x=yield_thr, ymin=0, ymax = 200, linewidth=2, color = 'r', linestyle = '--')
#             plt.hist(mean_values, bins = [0, 0.5, 1,2, 3, 4, 5,6,7,8,9,10])
#             extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
#             plt.legend([extra],('rate of vias < 1 Ohm : \n %.3f' %rel),bbox_to_anchor=(1, 1))
            r = unc.nominal_value(np.mean(low_mean))
            r2 = ufloat(r, 0.013)            
            box = AnchoredText(' vias $\leq$ 1 $\Omega$: %2.f %% \n mean R : %.2f $\pm 0.01$ $\Omega$' %(rel*100, r), loc=1)
            ax = plt.axes()
            ax.add_artist(box)
            
            plt.savefig('histogram-of-' + str(size) + 'FE-with-mean-and-uncertainties.pdf')
            plt.show()
            
    
    
    
        
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")


    workdir = '/media/niko/data/TSV-measurements'
    devices = [     '/media/niko/data/TSV-measurements/TSV-D7/resmeas-keithley2400',
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
    

                               
    '''
    just calculate resistances
    '''   
#     for i in devices:
#         count = 0
#         files = os.listdir(i)
#         for x in files:
# #             print i, x
#             if x.endswith('.csv'):
#                 res, unc, datafile = TSV_analysis().get_resistance_from_fit(os.path.join(i,x))
# #                 print res, unc
#                 resistances.append((res,unc))
#                 count +=1
#         logging.info('processed %r vias in %s' % (count,i))
#     resistances = np.array(resistances)
#     print 'Processed %r devices' % len(devices)
#     print 'median of resistances = %r $\pm $ %r' % (np.median(resistances[:,0]),np.median(resistances[:,1]))
    
    
    '''
    plotting single FE's
    '''
    all_res = []
    for i in devices:
        count = 0
        files = os.listdir(i)
        resistances = []
        for x in files:
            if x.endswith('.csv'):
                res, unc, datafile = TSV_analysis().get_resistance_from_fit(os.path.join(i,x))
                resistances.append((res,unc,float(datafile.split(os.sep)[-1].split('-')[0][3:]))) # last entry gives via number from datafile, needed for map
                count +=1
                all_res.append(resistances[-1])
        logging.info('processed %r vias in %s' % (count,i))
        resistances = np.array(resistances)
        TSV_analysis().plot_FE(i,resistances, plotmarker=2)
    all_res = np.array(all_res)
    print all_res.shape
    print 'Processed %r devices' % len(devices)
    print 'median of resistances = %r $\pm $ %r' % (np.median(all_res[:,0]),np.median(all_res[:,1]))
    
    
    '''scatter plot, histogram and yield of all vias'''
    
    
    
    