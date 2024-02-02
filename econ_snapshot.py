
from swamp.gbtsca import *
from swamp.gbtsca_transport import sca_transport_tester
from swamp.SlowControl_Interface import SlowControl_Interface
from lpgbt_control_lib.lpgbt_control_lib import LpgbtV1
from swamp import roc, ECON, lpgbt_i2c, sc_lpgbt, cfgconverter
import yaml
import sys
import re
from time import sleep 



lpgbt_address = 0x71

cfg = { 'broadcast_address' : 2 }
name = 'sct_ec'
from swamp import lpgbt_ic
transport = lpgbt_ic.lpgbt_ec(name=name,cfg=cfg)
transport.setLoggingLevel('ERROR')

cfg = { 'address' : lpgbt_address }
lpgbt = sc_lpgbt.sc_lpgbt(name='lpgbt',cfg=cfg)
lpgbt.setLoggingLevel('ERROR')
lpgbt.set_transport(transport)

bus = 1
cfg = { 'bus' : int(bus) }
transport_i2c = lpgbt_i2c.lpgbt_i2c(name='lpgbt.i2c',cfg=cfg)
transport_i2c.setLoggingLevel('ERROR')
transport_i2c.set_carrier(lpgbt)
master_cfg =  { 'clk_freq'           : 3, # { 0: 100 kHz, 1: 200 kHz, 2: 400 kHz, 3: 1 MHz }
                'scl_drive'          : False,
                'scl_pullup'         : False,
                'scl_drive_strength' : 0,
                'sda_pullup'         : False,
                'sda_drive_strength' : 0
           }
transport_i2c.configure(cfg=master_cfg)

#Instantiating the econ
econ = ECON.econ(name = 'ECON-T', cfg={
        'address': int('0x21',16),
        'path_to_json': 'swamp/regmaps/ECONT_I2C_params_regmap.json',
	'init_config': 'swamp/configs/econt_test_config.yaml',
        })
econ.set_transport(transport_i2c)
econ.setLoggingLevel('INFO')

config1 = {'RW':  {'CH_ALIGNER_*INPUT_ALL': {'registers': {'config': {'params': {'per_ch_align_en': {'param_value': 0}}}}},
                            'ALIGNER_ALL': {'registers': {'config': {'params': {'i2c_snapshot_en': {'param_value': 1},
                                                                                'snapshot_arm': {'param_value': 0},
                                                                                'snapshot_en': {'param_value': 1}}}}}}}

config2 = {'RW':  {'ALIGNER_ALL': {'registers': {'config': {'params': {'snapshot_arm': {'param_value': 1}}}}}}}

config3 = {'RW':  {'CH_ALIGNER_*INPUT_ALL': {'registers': {'config': {'params': {'per_ch_align_en': {'param_value': 1}}}}},
                            'ALIGNER_ALL': {'registers': {'config': {'params': {'i2c_snapshot_en': {'param_value': 0},
                                                                                'snapshot_en': {'param_value': 1}}}}}}}
econ.configure(config1)
econ.configure(config2)
econ.configure(config3)

config4 = {"ChAligner": {"00": {"snapshot": 1}, "01": {"snapshot": 1},  "02": {"snapshot": 1},  "03": {"snapshot": 1},  "04": {"snapshot": 1},  "05": {"snapshot": 1},  "06": {"snapshot": 1},  "07": {"snapshot": 1},
                         "08": {"snapshot": 1}, "09": {"snapshot": 1},  "10": {"snapshot": 1},  "11": {"snapshot": 1},  "12": {"snapshot": 1}}}

print(config4)
