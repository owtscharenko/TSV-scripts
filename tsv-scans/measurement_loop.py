import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import progressbar
import os.path

#from scan_misc import Misc 
from basil.dut import Dut


class IV(object):
    
    
    def __init__(self, conf):
            
        self.dut = Dut(conf)
        self.dut.init()
        #self.misc = Misc(dut=self.dut)  



    def measure_current(self, device, timeout,minimum_delay):
        
        was_above = False
        was_below = True
        
        current = float(self.dut[device].get_current())
        for i in range(timeout):
            time.sleep(minimum_delay)
            measurement = float(self.dut[device].get_current())
            if abs(measurement) > abs(current):
                was_above = True
            if abs(measurement) < abs(current):
                was_below = True
            if was_above and was_below:
                break
            if measurement == current:
                break
            current = measurement
            
        return measurement

    def measure_voltage(self, device, timeout, minimum_delay):
        
        was_above = False
        was_below = True
        
        voltage = float(self.dut[device].get_voltage())
        for i in range(timeout):
            time.sleep(minimum_delay)
            measurement = float(self.dut[device].voltage())
            if abs(measurement) > abs(voltage):
                was_above = True
            if abs(measurement) < abs(voltage):
                was_below = True
            if was_above and was_below:
                break
            if measurement == voltage:
                break
            voltage = measurement
            
        return measurement



    def scan_tsv_res_VOLT(self, file_name, max_Vin, current_limit, steps , stepsize, *device):
          
            logging.info("Starting ...")              
            self.dut['Sourcemeter'].on()
            self.data=[]
            fncounter=1                                                 #creates output .csv
            while os.path.isfile( file_name ):
                file_name = file_name.split('.')[0]
                file_name = file_name.split('_')[0]
                file_name = file_name + "_" + str(fncounter) + ".csv"
                fncounter = fncounter + 1
                              
            pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=max_Vin, poll=10, term_width=80).start()               #fancy progress bar
            with open(file_name, 'wb') as outfile:
                f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
                    
                f.writerow(['Input voltage [V]', 'Input current [A]', 'Resistance [ohm] '])                      #What is written in the output file
            
                input = 0
                counter = 0                                                                                 
                for x in range(0, int(steps)):                                                                                                                #loop over steps                                                                
                    self.dut['Sourcemeter'].set_voltage(input)
                    self.dut['Sourcemeter'].on()                                                                                                  #Set input current
                    input_voltage = self.measure_voltage('Sourcemeter', 100, 0.05)
                    #self.dut['Sourcemeter'].on()                                                                                       #Value of interest is in the [0] position of the readout list
                    input_current = self.measure_current('Sourcemeter', 100 , 0.05)    
                    resistance = input_voltage/input_current
                    logging.info("Set input voltage to %r" % input)
                    logging.info("Input current is %r A" % input_current)                                                                                           #Logging the readout
                    logging.info("Input voltage is %r V" % input_voltage)
#                     print 'resistance %r' % resistance                                                         #Writing readout in output file
                    if x > 0 and input_current > 0 :
                        self.data.append([input_voltage, input_current, resistance])                                                          #Writing readout in output file
                        f.writerow(self.data[-1])
                    elif input_current < 0:
                        print'warning: outside range! current = %f' % input_current
                    elif x == 0 :
                        print 'discarding first value'
                    if resistance > 1e5 :
                        counter +=1
                    pbar.update(input)
                    input += stepsize                                                                                                                             #Increase input current for next iteration
                    if input > max_Vin:
                        break
                    elif counter == 25:
                        print 'Resistance too high, aborting'
                        break
                    elif input_current >= current_limit:
                        print 'reached current limit! aborting'                                                                                                #Maximum values reached?
                        break     
                    elif counter > 0:
                        print 'counter = %i' % counter
                
                pbar.finish()
                self.dut['Sourcemeter'].off()
                logging.info('Measurement finished, plotting ...')
      
            return file_name#.split('.')[0]
        