#!/usr/bin/python

import sys
import uhal
import time
import numpy as np
import argparse

class Config(object):
    def __init__(self, lpgbt):
        self.lpgbt=lpgbt

    def connect(self):
        uhal.setLogLevelTo( uhal.LogLevel.ERROR )
        self.hw=uhal.ConnectionManager("file:///opt/cms-hgcal-firmware/hgc-test-systems/active/uHAL_xml/connections.xml").getDevice("TOP")
        self.link_capture = self.hw.getNode("{0}-capture-{0}-link-capture".format(self.lpgbt))
        self.link_capture_fifo = self.hw.getNode("{0}-capture-{0}-link-capture_FIFO".format(self.lpgbt))
        self.backend=self.hw.getNode("backend-scintillator-0")
        self.transceiver=self.hw.getNode("backend-transceiver-right-0")
        self.fastcmd=self.hw.getNode("Housekeeping-FastCommands-fastcontrol-axi-0")

    def singlelinkWrite(self, Name, val, linkNum, block):
        block.getNode("link{0}.{1}".format(linkNum,Name)).write(int(val))
        self.hw.dispatch()

    def linksWrite(self, Name,val, numLinks, block):
        for i in range(numLinks):
            block.getNode("link{0}.{1}".format(i,Name)).write(int(val))
        self.hw.dispatch()

    def lc_resetaqcuire(self):
        numLinks=self.link_capture.getNode("global.num_links").read()
        self.hw.dispatch()
        self.linksWrite("aquire_length", 0, numLinks, self.link_capture)
        self.linksWrite("total_length", 0, numLinks, self.link_capture)
        self.linksWrite("capture_mode_in", 0, numLinks, self.link_capture)
        self.linksWrite("L1A_offset_or_BX", 0, numLinks, self.link_capture)
        self.link_capture.getNode("global.continous_acquire").write(int(0))
        self.hw.dispatch()
        self.linksWrite("explicit_rstb_acquire", 0, numLinks, self.link_capture)
        self.hw.dispatch()

    def ConfigCommands(self):
        numLinks=self.link_capture.getNode("global.num_links").read()
        self.hw.dispatch()
        if self.lpgbt == "DAQ":
        #     self.singlelinkWrite("delay.bit_reverse", 1, 4, self.link_capture)
            # self.singlelinkWrite("delay.invert", 1, 4, self.link_capture)
            self.singlelinkWrite("delay.invert", 0, 2, self.link_capture)
            self.singlelinkWrite("delay.words_little_endian", 0, 2, self.link_capture)
            self.singlelinkWrite("delay.bytes_little_endian", 0, 2, self.link_capture)
            # self.singlelinkWrite("delay.bit_reverse", 1, 2, self.link_capture)
            self.hw.dispatch()
        # self.linksWrite("align_pattern", 2899102924, numLinks, self.link_capture)
        self.linksWrite("align_pattern", int("0xaccccccc", 16), numLinks, self.link_capture)
        # self.linksWrite("align_pattern", int("0xa1234567", 16), numLinks, self.link_capture)
        # self.linksWrite("align_pattern", int("0xa000ffff", 16), numLinks, self.link_capture)
        self.link_capture.getNode("global.explicit_align").write(int(1))
        self.hw.dispatch()
        # self.linksWrite("L1A_offset_or_BX", 0, numLinks, self.link_capture)
        if self.lpgbt == "DAQ":
            # example of single write:
            # self.singlelinkWrite("L1A_offset_or_BX", 25, 1, self.link_capture)
            self.linksWrite("L1A_offset_or_BX", 39, numLinks, self.link_capture)
            self.linksWrite("fifo_latency"    ,  0, numLinks, self.link_capture)
        if self.lpgbt == "trig":
            self.linksWrite("L1A_offset_or_BX", 39, numLinks, self.link_capture)
            self.linksWrite("fifo_latency"    ,  0, numLinks, self.link_capture)

        self.linksWrite("aquire_length", 45, numLinks, self.link_capture)
        self.linksWrite("total_length",  45, numLinks, self.link_capture)
        self.linksWrite("capture_mode_in", 2, numLinks, self.link_capture)
        self.link_capture.getNode("global.continous_acquire").write(int(63))
        self.hw.dispatch()

def main():
    trig = Config("trig")
    trig.connect()
    trig.lc_resetaqcuire()
    trig.ConfigCommands()

    daq = Config("DAQ")
    daq.connect()
    daq.lc_resetaqcuire()
    daq.ConfigCommands()

if __name__ == '__main__':
    main()

