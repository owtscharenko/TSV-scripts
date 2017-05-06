from measurement_loop import IV
from playing_with_plots import TSV_res_meas_analysis
from plot import LfCMOSplot
from basil.dut import Dut
import tables as tb
import csv

import logging
import os
import time
import numpy as np

output_file = '/media/niko/data/TSV-measurements/keithley2410-std-devs.csv'

dut = Dut('/home/niko/git/TSV-scripts/tsv_scans/devices.yaml')
dut.init()

dut['Sourcemeter'].beep_off()
dut['Sourcemeter'].display_off()
dut['Sourcemeter'].set_current_limit(0.205)
print 'SMU current limit is %r A' % dut['Sourcemeter'].get_current_limit()[:-1]

# with tb.open_file(output_file, 'w') as noise_occ_output_h5:
    
with open(output_file, 'wb') as outfile:
    f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
          
    f.writerow(['Input voltage [V]', 'Input current [A]', 'Std dev voltage ','Std dev current'])    
    global_current_dev = []
    global_voltage_dev = []
    
    for y in xrange(1,200,10):
        dut['Sourcemeter'].set_voltage(y*0.001)
        logging.info('set voltage to %r mV' %y)
        meas_c = []
        meas_v = []
        meas_test = []
        for x in xrange(0,100):
            i = float(dut['Sourcemeter'].get_current().split(',')[1])
            v = float(dut['Sourcemeter'].get_voltage().split(',')[0])
            meas_c.append(i)
            meas_v.append(v)
            meas_test.append((v,i))
            logging.info('voltage = %r' % v)
            logging.info('current = %r' % i)
            f.writerow((meas_v[-1],meas_c[-1],0,0))
#             time.sleep(0.01)
        logging.info('finished %r mV cycle calculating std.devs' % y)
        meas_c = np.array(meas_c)
        meas_v = np.array(meas_v)
        print 'separated arrays'
        print 'voltage dev = %r' %np.std(meas_v)
        print 'current dev = %r' %np.std(meas_c)
        print 'now fancy approach'
        meas_test = np.array(meas_test)
        voltage_dev = np.std(meas_test[:,0])
        current_dev = np.std(meas_test[:,1])
        print 'std. dev for Voltage measurement = %r' % voltage_dev
        print 'std. dev for Current measurement = %r' % current_dev
        global_voltage_dev.append(voltage_dev)
        global_current_dev.append(current_dev)
        f.writerow((0,0,voltage_dev,current_dev))
    f.writerow('mean std devs:')
    f.writerow((0,0,np.mean(global_voltage_dev),np.mean(global_current_dev)))
#         data = noise_occ_output_h5.create_carray(noise_occ_output_h5.root, name='values', title='Voltages and Currents used to determin Std. dev', atom=tb.Atom.from_dtype(meas_test.dtype), shape=meas_test.shape, filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
#         
#         c = noise_occ_output_h5.create_carray(noise_occ_output_h5.root.devs, name='Current', title='standard deviations for Current', atom=tb.Atom.from_dtype(current_dev.dtype), shape=(y,2), filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))  
#         v = noise_occ_output_h5.create_carray(noise_occ_output_h5.root.devs, name='Voltage', title='standard deviations for Voltage', atom=tb.Atom.from_dtype(voltage_dev.dtype), shape=(y,2), filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
#         data[:] = (meas_c, meas_v)
#         c[:] = (y,current_dev)
#         v[:] = (y,voltage_dev)

dut['Sourcemeter'].set_voltage(0)
dut['Sourcemeter'].off()