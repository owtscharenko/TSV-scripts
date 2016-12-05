from measurement_loop import IV
from playing_with_plots import TSV_res_meas_analysis

import logging
import os
import time
import numpy as np



if __name__ == '__main__':
                               
    via = 4
#     current = -0.02 # In Ampere
    voltage = 0.19  # In VOLT
    climit = 0.3 # In Ampere
    marker = False
    stepsize = 0.0005
        
    '''creating file name'''
#     if current > 0 and sensing:
#         f = 'via' + str(via) + '-' + str(int(current*1000)) + 'mamp-4wire.csv'
#     elif current > 0 and not sensing:
#         f = 'via' + str(via) + '-' + str(int(current*1000)) + 'mamp-2wire.csv'
#     elif voltage and sensing:
#         f = 'via' + str(via) + '-' + str(int(voltage*1000)) + 'mvolt-4wire.csv'
#         marker = True
#     elif voltage and not sensing:
#         f = 'via' + str(via) + '-' + str(int(voltage*1000)) + 'mvolt-2wire.csv'
#         marker = True
    
    f = 'via' + str(via) + '-' + str(int(climit*1000)) + 'mamp-4wire.csv'
    workdir = '/media/niko/data/TSV-measurements/TSV-S6/resmeas'
    os.chdir(workdir)
    '''
    Scanning
    '''
    iv = IV('/home/niko/git/TSV-scripts/tsv-scans/devices.yaml')
#     if current > 0 :    
#         iv.scan_tsv_res_source_CURR(f, current, 1, 5000 , 0.0001, sensing, 'Sourcemeter1')
#     elif current < 0 :
    file =  iv.scan_tsv_res_VOLT(f, voltage, climit, 5000 , stepsize, 'Sourcemeter')                                                                  
    '''
    Plotting
    '''   
    p = (1,5,7);
    func = TSV_res_meas_analysis()
#     print workdir, f
    x,y,z = func.load_file(os.path.join(workdir, file))     
    func.plot_single_via(x, y, z, p, marker)     
#     print func.mean_res_1_via(z)
    func.histo_1_via(z,60,'b')
    print ('mean resistance: %r ' % np.mean(z))
    logging.info('plotting finished')
          