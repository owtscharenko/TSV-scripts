'''
Created on 26.09.2016

Misc. script containing the methods used in remote operation of Keithley (source-)meters

@author: Florian
'''
import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import progressbar
import os.path

from basil.dut import Dut
from pyexpat import model

class Misc(object):
    
    def __init__(self, dut, max_current=1, minimum_delay=0.1):
        self.max_current = max_current
        self.minimum_delay = minimum_delay
        #self.devices=devices
        self.dut=dut
        self.data=[]
        
        
    
    
    def get_device_type(self, *device):
        '''
        Query device name. get_name() output looks like:
        KEITHLEY INSTRUMENTS INC.,MODEL 2410,1239506,C30   Mar 17 2006 09:29:29/A02  /H/J
        Extract vendor and model id to verify the meter specified in the devices.yaml.
        If needed, the used meters have to be added here (and/or in the devices.yaml).
        '''
        name_arr = [None]*len(device)
        type_arr = [None]*len(device)
        vendor = [None]*len(device)
        model = [None]*len(device)
        typ = [None]*len(device)
        for i in range(0, len(device)):
            name_arr[i] = str(self.dut[device[i]].get_name())
            if 'KEITHLEY' in name_arr[i]:
                vendor[i]= 'keithley'
                if 'MODEL 2410' in name_arr[i]:
                    model[i] = str(2410)
                elif 'MODEL 2400' in name_arr[i]:
                    model[i] = str(2400)
                elif 'MODEL 2000' in name_arr[i]:
                    model[i] = str(2000)
            else:
                raise RuntimeError('Something went wrong')
            typ [i] = vendor[i] + '_' + model[i]
            
        return typ
          
    #def get_current_reading(self, *device):
    def measure_current(self, *device):
        '''
        Current reading of a Keithley 2410 sourcemeter. Since querying the voltage/current reading results in a tuple,
        the proper element has to be selected. In case of the Keithley 2410 sourcemeter, the current reading is the second
        element of the tuple, the voltage reading the first element. If using a different (source-)meter, edit as needed.
        '''
        typ = 'keithley_2410'
        current = [None]*len(device)
        if typ == 'keithley_2410':
            for i in range(0, len(device)):
                #logging.info("Query results in %r" % dut[device[i]].get_current()) #Raw output of a current query. Used to determine which element of the output tuple represents the measured current.
                current[i] = float(self.dut[device[i]].get_current().split(',')[1])
            return current
        else:
            pass
        
    #===========================================================================            #Not working as intended
    # def measure_current(self, *device):
    #     '''
    #     Measures the current reading of the (source-/multi-)meter. List current[] contains the current measurements for i meters. 
    #     '''
    #     time.sleep(self.minimum_delay)
    #     current = [None]*len(device)
    #     
    #     #To-Do: Add a 'measurement delay' to ensure the reading is stable.
    #     
    #     for i in range (0, len(device)):
    #         current[i] = self.get_current_reading(*device)[i]
    #         if abs(current[i]) > abs(self.max_current) and current[i] < 1e37:
    #             raise RuntimeError('Maximum current with %e A reached, abort' % current[i])
    #     return current
    #===========================================================================
    
    #def get_voltage_reading(self, *device):
    def measure_voltage(self, *device):
        '''
        See get_current_reading().
        '''
        #typ = self.get_device_type(device)
        typ = 'keithley_2410'
        voltage = [None]*len(device)
        if typ == 'keithley_2410':
            for i in range(0, len(device)):
                voltage[i] = float(self.dut[device[i]].get_voltage().split(',')[0])
            return voltage
        else:
            pass
        
    #===========================================================================            #Not working as intended
    # def measure_voltage(self, *device):
    #     '''
    #     See measure_current()
    #     '''
    #     time.sleep(self.minimum_delay)
    #     voltage = [None]*len(device)
    #     
    #     #To-Do: Add a 'measurement delay' to ensure the reading is stable.
    #     
    #     for i in range(0, len(device)):
    #         voltage[i] = self.get_voltage_reading(*device)[0]
    #     return voltage
    #===========================================================================
    
    def set_source_mode(self, mode, limit1, limit2, limit3, *device):
        set_mode = [None]*len(device)
        limit = [limit1, limit2, limit3]
        for i in range(0, len(device)):
            self.dut[device[i]].off()
            set_mode [i] = str(self.dut[device[i]].get_source_mode())
            if 'VOLT' in set_mode[i]:
                self.dut[device[i]].set_current_limit(0.001)
                self.dut[device[i]].set_voltage(0)  
            elif 'CURR' in set_mode[i]:
                self.dut[device[i]].set_voltage_limit(0.001)
                self.dut[device[i]].set_current(0) 
            else:
                raise RuntimeError('Something went wrong 1')
            if 'VOLT' in mode:
                if limit[i] > 1:
                    logging.info("Something went wrong 2")
                    break
                else:
                    self.dut[device[i]].source_volt()
                    self.dut[device[i]].set_voltage(0)
                    self.dut[device[i]].set_current_limit(limit[i])                
            elif 'CURR' in mode:
                if limit[i] > 20:
                    logging.info("Something went wrong 3")
                    break
                else:
                    self.dut[device[i]].source_current()
                    self.dut[device[i]].set_voltage_limit(limit[i])
                    self.dut[device[i]].set_current(0)
            set_mode [i] = str(self.dut[device[i]].get_source_mode())
            
        return set_mode
    
    def reset(self, *device):
        '''Resetting the devices used. The sourcing function currently used should be given as 'mode'. Sets the compliance limit to 0 (V // A) and turns the output off.'''
        self.data = []
        set_mode = [None]*len(device)
        for i in range(0, len(device)):
            self.dut[device[i]].four_wire_off()
            self.dut[device[i]].set_autorange()
            set_mode[i] = str(self.dut[device[i]].get_source_mode())
            if 'VOLT' in set_mode[i]:
                self.dut[device[i]].set_current_limit(0.001)
                self.dut[device[i]].set_voltage(0)  
            elif 'CURR' in set_mode[i]:
                self.dut[device[i]].set_voltage_limit(0.001)
                self.dut[device[i]].set_current(0)
            else:
                return 'False'
            self.dut[device[i]].off() 
        return set_mode

            
    

if __name__ == '__main__':
    
    dut = Dut('devices.yaml')
    dut.init()
    print dut['Sourcemeter1'].get_name()
    print dut['Sourcemeter2'].get_name()
    print dut['Sourcemeter3'].get_name()
    
    misc = Misc(dut=dut)
    #print misc.get_voltage_reading('Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3')
    #===========================================================================
    # print misc.measure_voltage('Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3')
    #print misc.measure_current('Sourcemeter1')
    # print misc.get_device_type('Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3')
    # print misc.set_source_mode('VOLT',  .2,  .2, .2, 'Sourcemeter1', 'Sourcemeter3')
    # print misc.set_source_mode('CURR',  1,  1,  1, 'Sourcemeter2')
    #===========================================================================
    print misc.reset('Sourcemeter1', 'Sourcemeter2', 'Sourcemeter3')
    #dut['Sourcemeter3'].on()
    #print misc.set_source_mode('CURR', 2, 1.5, 1.5, 'Sourcemeter1', 'Sourcemeter2')


    
    