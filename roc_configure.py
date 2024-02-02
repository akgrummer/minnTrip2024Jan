
from swamp.gbtsca import *
from swamp.gbtsca_transport import sca_transport_tester
from swamp.SlowControl_Interface import SlowControl_Interface
from swamp import roc
import yaml
import sys

def simple_roc_read(i2c,page,reg):
    r0=((page<<5)|reg)&0xFF
    r1=page>>3
    i2c0.write(0b0101000, r0) # R0
    i2c0.write(0b0101001, r1) # R1
    val1 = i2c0.read(0b0101010) # Read the value of the register
    return val1&0xFF

def simple_roc_write(i2c,page,reg,val):
    r0=((page<<5)|reg)&0xFF
    r1=page>>3
    i2c0.write(0b0101000, r0) # R0
    i2c0.write(0b0101001, r1) # R1
    i2c0.write(0b0101010,val) # Write the value of the register

# Instantiate the Interface that connects to the hardware.
sc_interface = SlowControl_Interface()

cfg = {
    'sca_address': 0x00,
    'repl_address': 1,
    'sc_interface': sc_interface
}
print('SC Interface initialized')

transport = sca_transport_tester('sca-transport', cfg)
transport.setLoggingLevel("DEBUG")

transport.hdlc_reset()

sca = gbtsca('sca0', {'address': 0x01})
sca.set_transport(transport)

sca.enableADC()
adc_pin = sca.getADC(31)
sn = sca.getSerialNumber()
print("S/N %d   Internal temperature reference: %.1f C"%(sn,adc_pin.read_temperature()))



sca.enableGPIO()

ldo_enable = sca.getGPIO(22)
ldo_enable.set_dir(1)
ldo_softst = sca.getGPIO(23)
ldo_softst.set_dir(1)
hard_reset_pin = sca.getGPIO(2)
hard_reset_pin.set_dir(1)
soft_reset_pin = sca.getGPIO(4)
soft_reset_pin.set_dir(1)


ldo_enable.up()
ldo_softst.up()
soft_reset_pin.up()
hard_reset_pin.down()
hard_reset_pin.up()

roc_pll_lock = sca.getGPIO(0)
roc_error = sca.getGPIO(1)

print("ROC Status: \n  - PLL locked: {} \n  - Error: {}".format(
    roc_pll_lock.status(), roc_error.status()
))



sca.enableI2C()
i2c0 = sca.getI2C(0)
i2c0.enable()
i2c0.configure({"clk_freq": 1})
# val = i2c0.read(0b0101100)

#Instantiating the roc
aroc = roc.roc(name = 'roc', cfg={
	'address': int('0x28',16),
#        'regmapfile': 'swamp/regmaps/HGCROC3_sipm_I2C_params_regmap.csv',
	'regmapfile': 'swamp/regmaps/HGCROC3_sipm_I2C_params_regmap_dict.pickle',
#	'init_config': "swamp/configs/test_init_roc.yaml"
	})
aroc.set_transport(i2c0)
aroc.setLoggingLevel('INFO')

with open("swamp/configs/sipm_roc0_simple_init_aidan.yaml") as fin:
    config = yaml.safe_load(fin)
read_content = aroc.read(config)
print(read_content)

i2c0.write(0b0101000, 0b00001101) # R0
i2c0.write(0b0101001, 0b00000110) # R1

val1 = i2c0.read(0b0101010) # Read the value of the register

i2c0.write(0b0101000, 0b00001101) # R0
i2c0.write(0b0101001, 0b00000110) # R1

val2 = i2c0.read(0b0101010) # Read the value of the register

print(val1, val2)

print("Status: %02x"%simple_roc_read(i2c0,45,16))
print("FC lock count: %02x"%simple_roc_read(i2c0,45,17))
print("FC error count: %02x"%simple_roc_read(i2c0,45,18))
print("CTL0: %02x"%simple_roc_read(i2c0,45,0))

#simple_roc_write(i2c0,45,0,0x28)
aroc.configure(config)

roc_pll_lock = sca.getGPIO(0)
roc_error = sca.getGPIO(1)

print("ROC Status: \n  - PLL locked: {} \n  - Error: {}".format(
    roc_pll_lock.status(), roc_error.status()
))

read_content = aroc.read(config)
print(read_content)
