# Aidan's Visit to Minnesota


## ROC configuration

We instantiated a roc object in swamp. The wrapper script for swamp is similar to the file in this repo: [`roc_configure.py`](https://github.com/akgrummer/minnTrip2024Jan/blob/main/roc_configure.py)
- it does some GPIO resets
- uses the GBTSCA chip to communicate to the ROC over I2C
- reads an ADC on the SCA

To send a different configuration to the ROC, edit or use a different `yaml` [file](https://github.com/akgrummer/minnTrip2024Jan/blob/0fbd62700e72f98232240e462b07c43641f3d5e3/roc_configure.py#L92)


## ECON configuration

inital econ configuration was performed with `econ_configure.py` [here](https://github.com/akgrummer/minnTrip2024Jan/blob/main/econ_configure.py).

we used EC communcation to talk to the trigger lpbgt and i2c to talk the econ-T-P1:
transactor needs a broadcast address:
cfg = { 'broadcast_address' : 2 }
trigger lpgbt is on address 0x71
econ was on bus 1 of the lpgbt, and address `0x21`

Jeremy used a script to scan the i2c addresses in hgc-engine-tools. [i2c_scan_engine.py](https://gitlab.cern.ch/cms-hgcal-firmware/hgc-engine-tools/-/blob/c5f7c8ed54e23bd10f4b6bdc1e64216b064a7783/i2c_scan_engine.py)

## I2C snapshot

started to work on I2C snapshot configuration: `econ_snapshot.py`
from Danny's [link1](https://gitlab.cern.ch/hgcal-daq-sw/econd-sw/-/blob/master/econ_i2c.py?ref_type=heads#L201-300) - he said doesn't use swamp
from Danny's [link2](https://gitlab.cern.ch/cms-hgcal-firmware/hgc-engine-tools/-/blob/engineSetup_FNAL/econ_test.py?ref_type=heads#L266-284) - hesaid does use swamp.

From these links there should info on the sequence of parameter writes that are needed to take an I2C snapshot.

Inside the scripts of Danny's links there is also information on how to read the snapshot data.

Did not manage to complete this step while Aidan was here.


## Link Capture:

DAQ and trigger link captures can be performed with [uhal_backend_v3.py](https://github.com/akgrummer/minnTrip2024Jan/blob/main/uhal_backend_v3.py) after the links are configured with [configLCs.py](https://github.com/akgrummer/minnTrip2024Jan/blob/main/configLCs.py)


To print the status of the link capture parameters:
```
python uhal_backend_v3.py --status
```

To configure the LCs:
```
python configLCs.py
```

To send an L1A (and reprint the status, and see the fifo occupany values ):
```
python uhal_backend_v3.py --l1a
```

To read the fifo:
```
python uhal_backend_v3.py --fifo
```

there is a line added to the end of the --fifo protocol that resets the link capture links. This was needed because of a probable bug in the fw. This line
https://github.com/akgrummer/minnTrip2024Jan/blob/0fbd62700e72f98232240e462b07c43641f3d5e3/uhal_backend_v3.py#L333
should be removed if issue is resolved. The issue was that fifo on links 8-11 were automatically getting filled after the first l1a and no subsequent l1a. 

uhal_backend_v3.py also has other arguements for parsing the uhal dictionary and writing individual registers (has been useful for debugging).

This was tested on a DAQ capture for one link. TRIG links can also be configured with configLCs.py, but hasn't been tested on the motherboard system.


# python virtual environment in aidan's directory:
python venv setup:

python -m venv --system-site-packages ~/pyenv/tilebd

source ~/pyenv/tilebd/bin/active

## To remove packages Aidan installed:

delete this directory.
/home/agrummer/pyenv/tilebd

## installed packages in virtual environment:

### needed for billy's script (original version of roc_configure.py):

pip install nested_dict

### needed for uhal_backend_v3.py:

pip install tabulate

### needed for guiPEconD_backend_v3.py

pip install tk
but gui still doesn't work, need to install tkinter software

### for econ repo 1
[econ sw](https://gitlab.cern.ch/hgcal-daq-sw/econd-sw):
from Danny's [link](https://gitlab.cern.ch/hgcal-daq-sw/econd-sw/-/blob/master/econ_i2c.py?ref_type=heads#L201-300)
pip install bitstruct

### for econ repo 2: 
from Danny's [link2](https://gitlab.cern.ch/cms-hgcal-firmware/hgc-engine-tools/-/blob/engineSetup_FNAL/econ_test.py?ref_type=heads#L266-284)
pip install -r requirements.txt
(but was not successful)

### For swamp:

[pre-requisite](https://gitlab.cern.ch/hgcal-daq-sw/swamp#install-lpgbt_control_lib-pre-requisite) packages
this also wants to install matplotlib

Aidan did not manage to successfully install this prerequisite. Billy did the installation in his python virtual environment also - got error messages and ignored some of them. He managed to run swamp tools.

I’m afraid this install might require python3.9 - which is also a pain to install on centos7, but can be done from an online source, i.e. not on EPEL.
At Fermilab, I installed python3.9 - but could not install python versions > 3.9



