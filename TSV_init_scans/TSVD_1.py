# Script to test the IBL irradiation R&D samples
import os

from pybar.run_manager import RunManager  # importing run manager
from pybar.scans.scan_init import InitScan
from pybar.scans.test_register import RegisterTest
from pybar.scans.scan_digital_with_analog import DigitalScan
from pybar.scans.scan_analog import AnalogScan
from pybar.scans.tune_fei4 import Fei4Tuning
from pybar.scans.tune_stuck_pixel import StuckPixelScan
from pybar.scans.scan_threshold_fast import FastThresholdScan
from pybar.scans.tune_noise_occupancy import NoiseOccupancyScan


if __name__ == "__main__":   
    
    os.chdir('/media/niko/data/Niko/TSV-D1')
    target_threshold = 55  # in PlsrDAC (assuming 1 PlsrDAC = 55 electrons)
    target_charge = 1020  # in PlsrDAC (assuming 1 PlsrDAC = 55 electrons)
    target_tot = 3
    mask = 8
    gdac_mask = [3]
  
    runmngr = RunManager('configuration.yaml')
    runmngr.run_run(run=InitScan)  # to be able to set global register values

    # FE check and tuning
#     runmngr.run_run(run=RegisterTest)
    runmngr.run_run(run=DigitalScan, run_conf={'mask_steps' : mask})
    runmngr.run_run(run=AnalogScan, run_conf={'mask_steps' : mask, 'scan_parameters' : [('PlsrDAC', target_charge)]})  # heat up the Fe a little bit for PlsrDAC scan
#                       
#     runmngr.run_run(run=Fei4Tuning, run_conf={'target_threshold': target_threshold,
#                                               'target_tot': target_tot,
#                                               'target_charge': target_charge,
#                                               'mask_steps' : mask,
#                                               'enable_mask_steps_gdac' : gdac_mask,
#                                               'same_mask_for_all_dc' : True},
#                     catch_exception=False)
#     runmngr.run_run(run=AnalogScan, run_conf={'scan_parameters': [('PlsrDAC', target_charge)],'mask_steps' : mask})
#     runmngr.run_run(run=FastThresholdScan, run_conf={"ignore_columns":(), 'mask_steps' : mask})
#     runmngr.run_run(run=StuckPixelScan, run_conf={'mask_steps' : mask})
#     runmngr.run_run(run=NoiseOccupancyScan, run_conf={'occupancy_limit': 0,
#                                                       'n_triggers': 1000000})
