'''
Created on 26.09.2016

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import progressbar
import os.path

from scan_misc import Misc 
from basil.dut import Dut


class IV(object):
    
    
    def __init__(self, conf):
            
        self.dut = Dut(conf)
        self.dut.init()
        self.misc = Misc(dut=self.dut)  

    '''
    Class to perform a standard IV scan of the FE65 ShuLDO. For the standalone scan (current supply mode), one regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
    in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
    voltage drop due to R02 can be calculated using the input current and Ohm's law.
    The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21). 
    '''
    #===========================================================================
    # def __init__(self, max_current, minimum_delay=0.1):
    #     self.max_current = max_current
    #     self.minimum_delay = minimum_delay
    #     self.devices=devices
    #     self.data=[]
    #===========================================================================
    
    
    def scan_tsv_res_source_CURR(self, file_name, max_Iin, polarity, steps , stepsize, sense, *device):
        '''
        IV-scan in current supply mode. One regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
        in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
        voltage drop due to R02 can be calculated using the input current and Ohm's law.
        The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21).
        For a parallel scan, a second regulator is set to current supply mode. The maximum allowed input current has to be adjusted accordingly (x2).
        '''
        
        time.sleep(self.misc.minimum_delay)
        logging.info("Starting ...")
        
        self.misc.reset(*device)                                         #resetting the Sourcemeters
        self.misc.set_source_mode('CURR', 0.1, 1.5, 1.5, *device)          #set current source mode for every sourcemeter
        
        
        if sense == True:
            self.dut['Sourcemeter1'].four_wire_on()
#         elif sense ==  0:
#             dut['Sourcemeter1'].four_wire_off()
       # dut['Sourcemeter2'].four_wire_on()
        #dut['Sourcemeter3'].four_wire_on()

        fncounter=1                                                 #creates output .csv
        while os.path.isfile( file_name ):
            file_name = file_name.split('.')[0]
            file_name = file_name.split('_')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
            
            
        pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=max_Iin, poll=10, term_width=80).start()               #fancy progress bar
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
            #f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]', 'Regulator 2 output voltage [V]'])                      #What is written in the output file
            f.writerow(['Input voltage [V]', 'Input current [A]', 'Resistance [ohm] '])                      #What is written in the output file
        
            input = 0
            #print input                                                                                                                                         #Set input current to 0
            #input_current = self.misc.measure_current('Sourcemeter1')                                                                                                #Check input current
            for x in range(0, int(steps)):
                time.sleep(0.01)                                                                                                                      #loop over steps                                                                
                self.dut['Sourcemeter1'].set_current(polarity*input)                                                                                                  #Set input current
                time.sleep(0.01)
                input_current = self.misc.measure_current('Sourcemeter1')[0]                                                                                          #Value of interest is in the [0] position of the readout list
                time.sleep(0.01)
                input_voltage = self.misc.measure_voltage('Sourcemeter1')[0]
                resistance = input_voltage/input_current
                time.sleep(0.01)
                #output_voltage_2 = self.misc.measure_voltage('Sourcemeter3')[0]
                logging.info("Set input current to %r" % input)
                logging.info("Input current is %r A" % input_current)                                                                                           #Logging the readout
                logging.info("Input voltage is %r V" % input_voltage)
                print 'resistance %r' % resistance
                #logging.info("Regulator 1 output voltage is %r V" % output_voltage_1)
                #logging.info("Regulator 2 output voltage is %r V" % output_voltage_2)
                #self.misc.data.append([input_voltage, input_current, output_voltage_1, output_voltage_2])                                                          #Writing readout in output file
                if input_voltage>0:
                    self.misc.data.append([input_voltage, input_current, resistance])                                                          #Writing readout in output file
                    f.writerow(self.misc.data[-1])
                pbar.update(input)
                input += stepsize                                                                                                                               #Increase input current for next iteration
                if input > max_Iin or float(input_voltage) >= 0.1:                                                                                                #Maximum values reached?
                    break             
    
            
            
            pbar.finish()
            logging.info('Measurement finished, plotting ...')
            self.misc.reset(*device)            
        return file_name.split('.')[0]
 
    def scan_tsv_res_source_VOLT(self, file_name, max_Vin, current_limit, polarity, steps , stepsize, sense, *device):
        '''
        IV-scan in current supply mode. One regulator is operated in current supply mode (Jumper P7 // P8 // P9: bottom), the remaining regulators
        in voltage supply mode (Jumper P7 // P8 // P9: top). 'Sourcemeter1' supplys the input current. The input voltage is measured using 4-wire sensing between P01 (GND) and P03 (HI), the additional
        voltage drop due to R02 can be calculated using the input current and Ohm's law.
        The output voltage is measured via 4-wire sensing (Jumper P13 // P17 // P21).
        For a parallel scan, a second regulator is set to current supply mode. The maximum allowed input current has to be adjusted accordingly (x2).
        '''
        
        time.sleep(self.misc.minimum_delay)
        logging.info("Starting ...")
        
#         self.misc.reset(*device)                                         #resetting the Sourcemeters
        self.misc.set_source_mode('VOLT', current_limit, 1.5, 1.5, *device)          #set voltage source mode for every sourcemeter
        
#         if sense == True:
#             self.dut['Sourcemeter1'].four_wire_on()
#             print self.dut['Sourcemeter1'].get_remote_sense()
        self.dut['Sourcemeter1'].on()
#         elif sense ==  0:
#             self.dut['Sourcemeter1'].four_wire_off()        
       # self.dut['Sourcemeter2'].four_wire_on()
        #self.dut['Sourcemeter3'].four_wire_on()

        fncounter=1                                                 #creates output .csv
        while os.path.isfile( file_name ):
            file_name = file_name.split('.')[0]
            file_name = file_name.split('_')[0]
            file_name = file_name + "_" + str(fncounter) + ".csv"
            fncounter = fncounter + 1
            
            
        pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='*', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=max_Vin, poll=10, term_width=80).start()               #fancy progress bar
        with open(file_name, 'wb') as outfile:
            f = csv.writer(outfile ,quoting=csv.QUOTE_NONNUMERIC)
            #f.writerow(['Input voltage [V]', 'Input current [A]', 'Regulator 1 output voltage [V]', 'Regulator 2 output voltage [V]'])                      #What is written in the output file
            f.writerow(['Input voltage [V]', 'Input current [A]', 'Resistance [ohm] '])                      #What is written in the output file
        
            input = 0
            #print input                                                                                                                                         #Set input current to 0
            #input_current = self.misc.measure_current('Sourcemeter1')                                                                                                #Check input current
            for x in range(0, int(steps)):
                #time.sleep(0.05)                                                                                                                      #loop over steps                                                                
                self.dut['Sourcemeter1'].set_voltage(polarity*input)                                                                                                  #Set input current
                #time.sleep(0.05)
                input_current = self.misc.measure_current('Sourcemeter1')[0]                                                                                          #Value of interest is in the [0] position of the readout list
               #time.sleep(0.05)
                input_voltage = self.misc.measure_voltage('Sourcemeter1')[0]
                resistance = float(input_voltage)/float(input_current)
                #time.sleep(0.05)
                #output_voltage_2 = self.misc.measure_voltage('Sourcemeter3')[0]
                logging.info("Set input voltage to %r" % input)
                logging.info("Input current is %r A" % input_current)                                                                                           #Logging the readout
                logging.info("Input voltage is %r V" % input_voltage)
                print 'resistance %r' % resistance
                #logging.info("Regulator 1 output voltage is %r V" % output_voltage_1)
                #logging.info("Regulator 2 output voltage is %r V" % output_voltage_2)
                #self.misc.data.append([input_voltage, input_current, output_voltage_1, output_voltage_2])                                                          #Writing readout in output file
                if input_current>0:
                    self.misc.data.append([input_voltage, input_current, resistance])                                                          #Writing readout in output file
                    f.writerow(self.misc.data[-1])
                else :
                    print'outside range! %f' % input_current
                pbar.update(input)
                input += stepsize                                                                                                                               #Increase input current for next iteration
                if input > max_Vin or float(input_current) >= current_limit:                                                                                                #Maximum values reached?
                    break             
    
            
            
            pbar.finish()
            logging.info('Measurement finished, plotting ...')
#             self.misc.reset(*device)   
        return file_name#.split('.')[0]
  
if __name__ == '__main__':
    
#     dut = Dut('/home/niko/git/TSV-scripts/tsv-scans/devices.yaml')
#     dut.init()
#     misc = misc(dut=dut)  
                                                                                                                                        #Calling scan_self.misc with self.dut = Dut('devices.yaml')
    via = 1001
    sensing = True
    

    os.chdir('/media/niko/data/Niko/test_sm')
    
    iv = IV('/home/niko/git/TSV-scripts/tsv-scans/devices.yaml')
    iv.scan_tsv_res_source_CURR('via' + str(via) + '-20mamp-4wire.csv', 0.02, 1, 5000 , 0.0001, sensing, 'Sourcemeter1')
#     iv.scan_tsv_res_source_CURR('via' + str(via) + '-20mamp-2wire.csv', 0.02, 1, 5000 , 0.0001, sensing, 'Sourcemeter1')                                       #Conduct IV scan
#     iv.scan_tsv_res_source_VOLT('via' + str(via) + '-50mvolt-4wire.csv', 0.05, 1, 5000 , 0.0001, sensing,'Sourcemeter1')                                                                 
#     iv.scan_tsv_res_source_VOLT('via' + str(via) + '-50mvolt-2wire.csv', 0.05, 1, 5000 , 0.0001, sensing,'Sourcemeter1')