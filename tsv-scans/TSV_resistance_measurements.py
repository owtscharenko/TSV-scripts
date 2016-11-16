from resmeas import IV
from plots import TSV_res_meas_analysis

import logging
import os
import time



if __name__ == '__main__':

                                
    via = 1
    sensing = True
#     current = -0.02 # In Ampere
    voltage = 0.21  # In VOLT
    climit = 0.3 # In Ampere
    marker = True
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
    workdir = '/media/niko/data/Niko/TSV-D3/resmeas2'
    os.chdir(workdir)

    '''
    Scanning
    '''
    iv = IV('/home/niko/git/TSV-scripts/tsv-scans/devices.yaml')
#     if current > 0 :    
#         iv.scan_tsv_res_source_CURR(f, current, 1, 5000 , 0.0001, sensing, 'Sourcemeter1')
#     elif current < 0 :
    file =  iv.scan_tsv_res_source_VOLT(f, voltage, climit, 1, 5000 , stepsize, sensing, 'Sourcemeter1')                                                                  
    
    time.sleep(0.05)
    '''
    Plotting
    '''   
    func = TSV_res_meas_analysis()
#     print workdir, f
    x,y,z = func.load_file(os.path.join(workdir, file))
    
    func.plot_single_via(x, y, z, marker)     
#     print func.mean_res_1_via(z)
    func.histo_1_via(z,60,'b')
    logging.info('plotting finished')
          