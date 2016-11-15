from resmeas import IV
from plots import TSV_res_meas_analysis

import logging
import os




if __name__ == '__main__':

                                
    via = 99
    sensing = False
    current = 0.02
    voltage = 0.05
    
    '''creating file name'''
    if current > 0 and sensing:
        f = 'via' + str(via) + '-' + str(int(current*1000)) + 'mamp-4wire.csv'
    elif current > 0 and not sensing:
        f = 'via' + str(via) + '-' + str(int(current*1000)) + 'mamp-2wire.csv'
    elif voltage and sensing:
        f = 'via' + str(via) + '-' + str(int(voltage*1000)) + 'mvolt-4wire.csv'
    elif voltage and not sensing:
        f = 'via' + str(via) + '-' + str(int(voltage*1000)) + 'mvolt-2wire.csv'

    
    workdir = '/media/niko/data/Niko/TSV-D_3/resmeas'
   
    os.chdir(workdir)
    
    '''
    Scanning
    '''
    iv = IV('/home/niko/git/TSV-scripts/tsv-scans/devices.yaml')
    if current > 0 :    
        iv.scan_tsv_res_source_CURR(f, current, 1, 5000 , 0.0001, 1, 'Sourcemeter1')
    elif current < 0 :
        iv.scan_tsv_res_source_VOLT(f, voltage, 1, 5000 , 0.0001, 1,'Sourcemeter1')                                                                  


    quit()
    
    '''
    Plotting
    '''   
    func = TSV_res_meas_analysis()
    x,y,z = func.load_file(os.path.join(workdir, f))
    
#     func.plot_single_via(x, y, z)     
#     print func.mean_res_1_via(z)
    func.histo_1_via(z,'fd')
          