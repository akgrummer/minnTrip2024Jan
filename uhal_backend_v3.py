#!/home/agrummer/pyenv/tilebd/bin/python

import sys
import argparse
import uhal
import time
import numpy as np
from tabulate import tabulate
from smbus2 import SMBus, i2c_msg

def linksRead(Name, hexNum=False):
    numLinks=link_capture.getNode("global.num_links").read()
    hw.dispatch()
    for i in range(numLinks):
        val = link_capture.getNode("link{0}.{1}".format(i,Name)).read()
        hw.dispatch()
        if hexNum:
            print("{0} link {1},: {2}".format(Name, i, hex(val)))
        else:
            print("{0} link {1},: {2}".format(Name, i, val))
    
def linksWrite(Name,val):
    numLinks=link_capture.getNode("global.num_links").read()
    hw.dispatch()
    for i in range(numLinks):
        link_capture.getNode("link{0}.{1}".format(i,Name)).write(int(val))
        hw.dispatch()

def getAttributes(Name, node=None):
    listofMethods = ["getAddress", "getMask","getPermission", "getDescription"]
    if node is None: 
        myinst = hw.getNode(Name)
    else:
        myinst = hw.getNode(Name).getNode(node)
    funcs = [ hex, hex, str, str]
    rawList = [getattr(myinst, i)() for i in listofMethods]
    hw.dispatch()
    formattedList = [f(a) for f, a in zip(funcs, rawList)]
    vecval=np.column_stack((listofMethods,formattedList))
    table = tabulate(vecval, showindex=True, tablefmt="simple")
    print(table)

def globalLinksRead(Name, hexNum=False):
    numLinks=link_capture.getNode("global.num_links").read()
    hw.dispatch()
    for i in range(numLinks):
        val = link_capture.getNode("global.{0}.link{1}".format(Name,i)).read()
        hw.dispatch()
        if hexNum:
            print("{0} link {1}: {2}".format(Name, i, hex(val)))
        else:
            print("{0} link {1}: {2}".format(Name, i, val))
    
def globalLinksWrite(Name,val):
    numLinks=link_capture.getNode("global.num_links").read()
    hw.dispatch()
    for i in range(numLinks):
        link_capture.getNode("global.{0}.link{1}".format(Name,i)).write(int(val))
        hw.dispatch()

def globalRead(Name, hexNum=False):
    val = link_capture.getNode("global.{0}".format(Name)).read()
    hw.dispatch()
    if hexNum:
        print("{0}: {1}".format(Name, hex(val)))
    else:
        print("{0}: {1}".format(Name, val))
    
def globalWrite(Name,val):
    link_capture.getNode("global.{0}".format(Name)).write(int(val))
    hw.dispatch()

def genericRead(Name, hexNum=False):
    val = link_capture.getNode("{0}".format(Name)).read()
    hw.dispatch()
    if hexNum:
        print("{0}: {1}".format(Name, hex(val)))
    else:
        print("{0}: {1}".format(Name, val))
    
def genericWrite(Name,val):
    link_capture.getNode("{0}".format(Name)).write(int(val))
    hw.dispatch()

def getStatusArrayLinks(link_capture, Name, numLinks):
    m = np.array([str(Name)])
    for i in range(numLinks):
        val = link_capture.getNode("link{}.{}".format(i,Name)).read()
        hw.dispatch()
        m = np.append(m,int(val))
    return m

def getStatus(link_capture, LCname):
    numLinks=link_capture.getNode("global.num_links").read()
    hw.dispatch()
    nNames=["capture_mode_in", "capture_L1A", "aquire_length","total_length","status.link_aligned","link_aligned_count","link_error_count","walign_state","status.waiting_for_trig","fifo_occupancy",
    # "capture_SPARE_0",
    # "capture_SPARE_1",
    # "capture_SPARE_2",
    # "capture_SPARE_3",
    # "capture_SPARE_4",
    # "capture_SPARE_5",
    # "capture_SPARE_7",
    # "capture_extra",
    # "capture_OrbitCountReset",
    # "capture_EventBufferReset",
    # "capture_SPARE_6",
    # "capture_linkreset_ROCt",
    # "capture_EventCountReset",
    # "capture_ChipSync",
    # "capture_CalibrationReq_ext",
    # "capture_CalibrationReq_int",
    # "capture_NonZeroSuppress",
    # "capture_L1A",
    # "capture_orbitSync",
    # "capture_mode_in"
    ]
    # headers = np.array(["","link 0","link 1"])
    headers = np.array(["link {}".format(x) for x in range(numLinks)], dtype=object)
    headers = np.insert(headers, 0, LCname, axis=0)
    Name="link_enable"
    m = np.array([str(Name)])
    for i in range(numLinks):
        val = link_capture.getNode("global.{}.link{}".format(Name,i)).read()
        hw.dispatch()
        m = np.append(m,int(val))
    m = np.stack((headers,m))
    for i,Name in enumerate(nNames):
        # if i==0:
        #     m = getStatusArrayLinks(Name,numLinks)
        #     m = np.stack((headers,m))
        # else:
        n2 = getStatusArrayLinks(link_capture,Name,numLinks)
        m = np.concatenate((m,[n2]))
    table = tabulate(m, tablefmt="simple",headers="firstrow")
    print(table)

def reset(link_capture):
    linksWrite("aquire_length", 0)
    linksWrite("total_length", 0)
    linksWrite("capture_mode_in", 0)
    linksWrite("L1A_offset_or_BX", 0)
    link_capture.getNode("global.continous_acquire").write(int(0))
    hw.dispatch()
    linksWrite("explicit_resetb", 0)
    hw.dispatch()
    linksWrite("explicit_rstb_acquire",0)
    hw.dispatch()

def readFIFO(LC, LCfifo, Name, quiet):
    numLinks=LC.getNode("global.num_links").read()
    print("Aidan,", numLinks)
    hw.dispatch()
    # numLinks=1
    headers = np.array(["link {}".format(x) for x in range(numLinks)], dtype=object)
    bLength=[LC.getNode("link{0}.fifo_occupancy".format(i)).read() for i in range(numLinks)]
    hw.dispatch()
    maxLength = max(bLength)
    for i in range(numLinks):
        if i==0:
            #bLength=LC.getNode("link{0}.fifo_occupancy".format(i)).read()
            #hw.dispatch()
            if bLength[i] == 0:
                vecval = np.empty((maxLength,1))
                vecval[:] = np.NaN
                continue
            vecval = LCfifo.getNode("link{0}".format(i)).readBlock(bLength[i])
            hw.dispatch()
            # vecval=[hex(x)[2:] for x in vecval]
            vecval=["{0:08x}".format(x) for x in vecval]
        else:
            #bLength=LC.getNode("link{0}.fifo_occupancy".format(i)).read()
            #hw.dispatch()
            if bLength[i] == 0:
                vecval2 = np.empty((maxLength,1))
                vecval2[:] = np.NaN
                vecval=np.column_stack((vecval,vecval2))
                continue
            vecval2 = LCfifo.getNode("link{0}".format(i)).readBlock(bLength[i])
            hw.dispatch()
            vecval2=["{0:08x}".format(x) for x in vecval2]
            vecval=np.column_stack((vecval,vecval2))
    # print(vecval)
    if quiet:
        print("cleared fifo")
    elif maxLength>0:
        table = tabulate(vecval,headers,showindex=True, tablefmt="simple")
        print(table)
    else:
        print("no fifo data found")

parser=argparse.ArgumentParser(description="read and write uhal strings")
parser.add_argument('--node',type=str, default=None,help='give the name of the node')
parser.add_argument('--links',type=str, default=None,help='give the name of the node for links interaction')
parser.add_argument('--val',type=str, default=None, help='enter a value for the node (must use node option)')
# parser.add_argument('--ls',default=False, help='print the node names')
parser.add_argument('--ls', action='store_true', default=False, help='print the node names')
parser.add_argument('--lsval', action='store_true', default=False, help='print the node names and values')
parser.add_argument('--lsblocks', action='store_true', default=False, help='print the node names and values')
parser.add_argument('--lsall', action='store_true', default=False, help='print the node names')
parser.add_argument('--myhex', action='store_true', default=False, help='print the node names')
parser.add_argument('-q', '--quiet', action='store_true', default=False, help='quiet output mode')
parser.add_argument('-s', '--status', action='store_true', default=False, help='print the node names')
# parser.add_argument('-b','--block',type=str, default="link-capture-AXI-0", help='input the link capture block')
parser.add_argument('-b','--block',type=str, help='input the link capture block')
parser.add_argument('--fifo',  action='store_true',default=False, help='print the fifo vector')
parser.add_argument('--atts', action='store_true', default=False, help='print attributes')
parser.add_argument('--trig', action='store_true', default=False, help='print attributes')
parser.add_argument('--reset', action='store_true', default=False, help='print attributes')
parser.add_argument('--l1a', action='store_true', default=False, help='print attributes')


args=parser.parse_args()

uhal.setLogLevelTo( uhal.LogLevel.ERROR )
# uhal.setLogLevelTo( uhal.LogLevel.NOTICE )

# hw=uhal.ConnectionManager("file://connections.xml").getDevice("TOP")
# hw=uhal.ConnectionManager("file://connections.xml").getDevice("interposer")
# hw=uhal.ConnectionManager("file://address_table/connection.xml").getDevice("interposer")
hw=uhal.ConnectionManager( "file://"+"/opt/cms-hgcal-firmware/hgc-test-systems/active/uHAL_xml/connections.xml").getDevice("TOP")
# hw=uhal.ConnectionManager( "file://"+"/srv/hgcal/active/uHAL_xml/connections.xml").getDevice("TOP")
# hw=uhal.ConnectionManager("file://connections.xml").getDevice("TOP")
# hw=uhal.ConnectionManager("file://connections.xml").getDevice("interposer")
# backend=hw.getNode("backend")
# backend.getNode("CTL")
# frontend=hw.getNode("frontend") # need to handle possible no-front-end cases

# device_id = hw.id()
# print (hw)
# # Grab the device's URI
# device_uri = hw.uri()
# print(device_uri)

# link_capture = hw.getNode("link-capture-AXI-0")

if args.trig: lpgbt = "trig"
else: lpgbt="DAQ" 

# block = "link-capture-AXI-0"
block = "{0}-capture-{0}-link-capture".format(lpgbt)

if args.block == "fc":
    block = "Housekeeping-FastCommands-fastcontrol-axi-0"
elif args.block:
    block = args.block

link_capture = hw.getNode(block)
link_capture_FIFO = hw.getNode("{0}-capture-{0}-link-capture_FIFO".format(lpgbt))
fastcmd = hw.getNode("Housekeeping-FastCommands-fastcontrol-axi-0")

if args.node:
    list_of_node_ids = link_capture.getNode("{0}".format(args.node)).getNodes()
else:
    list_of_node_ids = link_capture.getNodes()
list_of_all_node_ids = hw.getNodes()

if args.l1a:
    print("sending one L1A")
    fastcmd.getNode("command.global_l1a_enable").write(1)
    hw.dispatch()
    fastcmd.getNode("periodic0.request").write(1)
    hw.dispatch()
    fastcmd.getNode("command.global_l1a_enable").write(0)
    hw.dispatch()
    l1aval = fastcmd.getNode("counters.l1a").read()
    hw.dispatch()
    print("total L1A cnt: {}".format(l1aval))
    getStatus(link_capture, "{0} links".format(lpgbt))

if args.lsval:
    vals = []
    for i in range(len(list_of_node_ids)):
        vals.append(link_capture.getNode("{0}".format(list_of_node_ids[i])).read())
    hw.dispatch()
    for i in range(len(list_of_node_ids)):
        print("{0}: {1}".format(list_of_node_ids[i], vals[i]))
    sys.exit()

if args.ls:
    for i in range(len(list_of_node_ids)):
        print("{0}".format(list_of_node_ids[i]))
    sys.exit()

if args.lsblocks:
    for i in range(len(list_of_node_ids)):
        if "." in list_of_node_ids[i]: continue
        print("{0}".format(list_of_node_ids[i]))
    sys.exit()

if args.lsall:
    #list_of_all_node_ids= [ x for x in list_of_node_ids ]
    for i in range(len(list_of_all_node_ids)):
        if "." in list_of_all_node_ids[i]: continue
        print(list_of_all_node_ids[i])
    sys.exit()

if args.atts:
    if args.node:
        getAttributes(block, args.node)
    else:
        getAttributes(block)
    sys.exit()

if args.node is not None:
    if args.val is not None:
        genericWrite(args.node, args.val)
        genericRead(args.node)
    else:
        if args.myhex:
            genericRead(args.node, args.myhex)
        else:
            genericRead(args.node)

if args.links is not None:
    if args.val is not None:
        args.val = int(args.val, 0)
        linksWrite(args.links, args.val)
        linksRead(args.links)
    else:
        if args.myhex:
            linksRead(args.links, args.myhex)
        else:
            linksRead(args.links)
if args.reset:
    reset(link_capture)

if args.status:
    getStatus(link_capture, "{0} links".format(lpgbt))

if args.fifo:
   readFIFO(link_capture, link_capture_FIFO, args.fifo, args.quiet) 
   linksWrite("explicit_rstb_acquire", 0)


