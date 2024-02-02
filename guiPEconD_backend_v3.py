#!/usr/bin/env python

import sys
import os
import tkinter as tk
from tkinter import ttk
import uhal
import time
import numpy as np
from tabulate import tabulate
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from queue import Queue
import threading
import subprocess

class tButton(object):
    def __init__(self,window, text, column, row, queue, command, shell=False):
        self.window = window
        self.text = text
        self.column = column
        self.row = row
        self.queue = queue
        self.command = command
        self.shell = shell
        self.red = "#DC143C"
        self.blue = "#6F8FAF"
        self.btn_text = tk.StringVar()
        self.btn_text.set("Start " + self.text)
        self.button = tk.Button(self.window, textvariable=self.btn_text, command=self.startThread)
        # self.button['bg'] = 'red'
        self.button.grid(column=self.column, row=self.row, sticky="NSEW")
        self.processFlag = threading.Event()

    def __del__(self):
        # print("called tButton destructor")
        if self.servpoll is None:
            self.serveroutput.terminate()
            # self.queue.put('stopped '+self.text+ ' server' +'\n')
            print('stopped'+self.text+ 'server')
            # self.text_STDOUT.insert(tk.END, "stopped server")
            # self.queue.put("stopped server")
            # self.serverLabel.config(text="server stopped")

    def startThread(self):
        msg = "pressed: " +self.text
        self.queue.put(msg)
        self.serverThread = threading.Thread(target=self.startProcess, args=[])
        self.serverThread.daemon = True # die when the main thread dies
        self.serverThread.start()
        self.btn_text.set("Stop " + self.text + " thread")
        self.button.configure(bg = self.blue, activebackground=self.blue, command = self.stopProcess)

    def startProcess(self):
        self.processFlag.clear()
        self.serveroutput = subprocess.Popen(self.command, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,universal_newlines=True)
        self.servpoll = self.serveroutput.poll()
        # if self.servpoll is None:
            # self.serverLabel.config(text="server on")
        while self.servpoll is None:
            if self.processFlag.is_set():
                break
            msg = self.serveroutput.stdout.readline()# .strip()  # read a line from the process output
            if msg:
                self.queue.put(msg)
            time.sleep(0.2)

    def stopProcess(self):
        # print("stop tButton Process")
        self.queue.put('pressed stop ' + self.text)
        self.processFlag.set()
        if hasattr(self, 'servpoll'):
            if self.servpoll is None:
                self.serveroutput.terminate()
                # print('stopped tButton server')
                self.queue.put('stopped '+ self.text+ ' process')
        if hasattr(self, 'serverThread'):
            # print("waiting on thread")
            self.serverThread.join()
            self.serveroutput = None
            self.servpoll = 1
            self.queue.put('stopped '+ self.text + ' thread')
        self.button.configure(bg = self.red, activebackground = self.red, command = self.startThread)

class CoreGUI(object):
    def __init__(self,window):
        self.window = window
        # uhal.setLogLevelTo( uhal.LogLevel.ERROR )
        uhal.setLogLevelTo( uhal.LogLevel.WARNING )
        # self.hw=uhal.ConnectionManager("file:///opt/cms-hgcal-firmware/hgc-test-systems/zcu102-siengine-v1p0/uHAL_xml/connections.xml").getDevice("TOP")
        self.hw=uhal.ConnectionManager("file:///opt/cms-hgcal-firmware/hgc-test-systems/active/uHAL_xml/connections.xml").getDevice("TOP")
        # self.hw=uhal.ConnectionManager("file:///srv/hgcal/fw-2023Mar31/uHAL_xml/connections.xml").getDevice("TOP")
        # self.hw=uhal.ConnectionManager("file:///srv/hgcal/active/uHAL_xml/connections.xml").getDevice("TOP")
        # self.hw=uhal.ConnectionManager('file:///srv/hgcal/fw-2023May23_1/uHAL_xml/connections.xml').getDevice("TOP")
        # self.link_capture = self.hw.getNode("link-capture-AXI-0")
        self.lpgbt = "trig"
        # self.lpgbt = "DAQ"
        self.link_capture = self.hw.getNode("{0}-capture-{0}-link-capture".format(self.lpgbt))
        # self.link_capture_fifo = self.hw.getNode("link-capture-AXI-0_FIFO")
        self.link_capture_fifo = self.hw.getNode("{0}-capture-{0}-link-capture_FIFO".format(self.lpgbt))
        self.backend=self.hw.getNode("enginev3-backend-0")
        # self.fastcmd=self.hw.getNode("fastcontrol-axi-0")
        # self.backend=self.hw.getNode("backend")
        self.fastcmd=self.hw.getNode("Housekeeping-FastCommands-fastcontrol-axi-0")

        tk.Grid.rowconfigure(self.window,0,weight=0)
        tk.Grid.columnconfigure(self.window,0,weight=1)
        tk.Grid.columnconfigure(self.window,1,weight=1)
        tk.Grid.columnconfigure(self.window,2,weight=1)
        tk.Grid.columnconfigure(self.window,3,weight=1)
        tk.Grid.columnconfigure(self.window,4,weight=1)
        tk.Grid.columnconfigure(self.window,5,weight=0)
        # tk.Grid.columnconfigure(self.window,6,weight=1)
        tk.Grid.rowconfigure(self.window,1,weight=1)
        tk.Grid.rowconfigure(self.window,2,weight=0)
        tk.Grid.rowconfigure(self.window,3,weight=0)
        tk.Grid.rowconfigure(self.window,4,weight=0)
        tk.Grid.rowconfigure(self.window,5,weight=0)
        tk.Grid.rowconfigure(self.window,6,weight=0)
        tk.Grid.rowconfigure(self.window,7,weight=0)

        self.label = tk.Label(self.window, text="Train 1", font=("Arial",30)).grid(row=0, columnspan=6)
        self.style = ttk.Style()
        self.style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Courier', 13)) # Modify the font of the body
        self.style.configure("mystyle.Treeview.Heading", font=('Calibri', 13,'bold')) # Modify the font of the headings
        self.style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders
        self.style.configure('Treeview', rowheight=30)
        # self.cols = ("link0", "link1", "link2", "link3", "link4", "link5")
        self.cols = ("link0", "link1", "link2", "link3", "link4", "link5", "link6", "link7", "link8", "link9", "link10", "link11", "link12", "link13")
        self.nNames=("capture_mode_in","aquire_length","status.link_aligned","link_aligned_count","link_error_count","walign_state","status.waiting_for_trig","fifo_occupancy")

        self.listBox = ttk.Treeview(self.window, style="mystyle.Treeview", columns=self.cols, show='tree headings')
        # set column headings
        self.listBox.heading("#0", text="Input Links")
        self.listBox.column("#0", minwidth=0, width=275, stretch=tk.NO)

        for col in self.cols:
            self.listBox.heading(col, text=col)    
            self.listBox.column(col, minwidth=0, width=70)

        self.listBox.grid(row=1, column=0, columnspan=6, sticky="NSEW")

        self.scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.listBox.yview)
        self.listBox.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=6, sticky='ns')

        self.label = tk.Label(self.window, text="" )
        self.label.grid(row=4, column=3, sticky="NSEW")
        self.btn_showStatus = tk.Button(self.window, text="refresh status", width=15, command=self.getStatus).grid(row=5, column=0, sticky="NSEW")
        self.btn_zcustatus = tk.Button(self.window, text="zcustatus", width=15, command=self.zcu_status)
        self.btn_zcustatus.grid(row=5, column=1, sticky="NSEW")
        self.btn_setrefclk = tk.Button(self.window, text="set ref clk", width=15, command=self.zcu_setrefclk)
        # btn_loadfw = tk.Button(self.window, text="Load FW", width=15, command=self.cmd_loadfw)
        # btn_loadfw.grid(row=8, column=1, sticky="NSEW")
        self.btn_setrefclk.grid(row=6, column=1, sticky="NSEW")
        self.btn_resetlink = tk.Button(self.window, text="reset link", width=15, command=self.zcu_resetlink)
        self.btn_resetlink.grid(row=7, column=1, sticky="NSEW")

        self.btn_fc_rocdreset = tk.Button(self.window, text="rocd reset", width=15, command=self.fc_rocd_reset)
        self.btn_fc_rocdreset.grid(row=5, column=2, sticky="NSEW")
        self.btn_fc_singleL1A = tk.Button(self.window, text="send one L1A", width=15, command=self.fc_singleL1A)
        self.btn_fc_singleL1A.grid(row=6, column=2, sticky="NSEW")
        self.labelrocdreset = tk.Label(self.window, text="" )
        self.labelrocdreset.grid(row=7, column=2, sticky="NSEW")
        self.labelL1A = tk.Label(self.window, text="" )
        self.labelL1A.grid(row=8, column=2, sticky="NSEW")

        self.btn_text = tk.StringVar()
        self.btn_text.set("Config Backend")
        self.ConfigButton = tk.Button(self.window, textvariable=self.btn_text, bg='#6F8FAF', activebackground="#6F8FAF", width=15, command=self.ConfigCommands)
        self.ConfigButton.grid(row=6, column=0, sticky="NSEW")
        self.btn_resetAqcuire = tk.Button(self.window, text="reset aqcuire", width=15, command=self.lc_resetaqcuire)
        self.btn_resetAqcuire.grid(row=7, column=0, sticky="NSEW")
        self.btn_readFIFO = tk.Button(self.window, text="read fifo", width=15, command=self.readFIFO)
        self.btn_readFIFO.grid(row=8, column=0, sticky="NSEW")

        self.var_Link0Offset = tk.IntVar()
        self.var_Link0Offset.set(27)
        self.label_Link0Offset = tk.Label(self.window, text="Link 0 Offset: ", anchor="e")
        self.entry_Link0Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link0Offset)
        self.label_Link0Offset.grid(row=5, column=4, sticky="NSEW")
        self.entry_Link0Offset.grid(row=5, column=5, sticky="NS")

        self.var_Link1Offset = tk.IntVar()
        self.var_Link1Offset.set(27)
        self.label_Link1Offset = tk.Label(self.window, text="Link 1 Offset: ", anchor="e")
        self.entry_Link1Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link1Offset)
        self.label_Link1Offset.grid(row=6, column=4, sticky="NSEW")
        self.entry_Link1Offset.grid(row=6, column=5, sticky="NS")

        self.var_Link2Offset = tk.IntVar()
        self.var_Link2Offset.set(27)
        self.label_Link2Offset = tk.Label(self.window, text="Link 2 Offset: ", anchor="e")
        self.entry_Link2Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link2Offset)
        self.label_Link2Offset.grid(row=7, column=4, sticky="NSEW")
        self.entry_Link2Offset.grid(row=7, column=5, sticky="NS")

        self.var_Link3Offset = tk.IntVar()
        self.var_Link3Offset.set(27)
        self.label_Link3Offset = tk.Label(self.window, text="Link 3 Offset: ", anchor="e")
        self.entry_Link3Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link3Offset)
        self.label_Link3Offset.grid(row=8, column=4, sticky="NSEW")
        self.entry_Link3Offset.grid(row=8, column=5, sticky="NS")

        self.var_Link4Offset = tk.IntVar()
        self.var_Link4Offset.set(27)
        self.label_Link4Offset = tk.Label(self.window, text="Link 4 Offset: ", anchor="e")
        self.entry_Link4Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link4Offset)
        self.label_Link4Offset.grid(row=9, column=4, sticky="NSEW")
        self.entry_Link4Offset.grid(row=9, column=5, sticky="NS")

        self.var_Link5Offset = tk.IntVar()
        self.var_Link5Offset.set(27)
        self.label_Link5Offset = tk.Label(self.window, text="Link 5 Offset: ", anchor="e")
        self.entry_Link5Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link5Offset)
        self.label_Link5Offset.grid(row=10, column=4, sticky="NSEW")
        self.entry_Link5Offset.grid(row=10, column=5, sticky="NS")

        self.var_Link6Offset = tk.IntVar()
        self.var_Link6Offset.set(27)
        self.label_Link6Offset = tk.Label(self.window, text="Link 6 Offset: ", anchor="e")
        self.entry_Link6Offset= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_Link6Offset)
        self.label_Link6Offset.grid(row=11, column=4, sticky="NSEW")
        self.entry_Link6Offset.grid(row=11, column=5, sticky="NS")

        self.var_CapLen = tk.IntVar()
        self.var_CapLen.set(45)
        self.label_CapLen = tk.Label(self.window, text="Cap. Len.:", anchor="e")
        self.entry_CapLen= ttk.Entry(self.window,font=('Courier',13,'normal'),width=4, text=self.var_CapLen)
        self.label_CapLen.grid(row=4, column=4, sticky="NSEW")
        self.entry_CapLen.grid(row=4, column=5, sticky="NS")

        self.closeButton = tk.Button(self.window, text="Close", width=10, command=self.on_exit).grid(row=0, column=4)
        self.window.bind('<Control-x>',lambda event:self.on_exit())

        self.listBox.bind("<Double-1>", self.OnDoubleClick) # double click
        self.window.bind('<Control-c>',lambda event:self.ConfigCommands())# event is passed to function, the .bind takes a function with one argument

        self.text_STDOUT = tk.Text(self.window, height=10)
        self.text_STDOUT.grid(row=12, column=0, sticky="NSEW", columnspan=6)
        self.scrollbar_STDOUT = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.text_STDOUT.yview)
        self.scrollbar_STDOUT.grid(row=12, column=6, sticky='nsew')
        self.text_STDOUT['yscrollcommand'] = self.scrollbar_STDOUT.set

        self.queue = Queue()
        self.StopTerminal = threading.Event()
        self.ClientEvent = threading.Event()
        self.terminalThread = threading.Thread(target=self.printer, args=[self.text_STDOUT])
        self.terminalThread.daemon = True
        # self.terminalThread = Process(target=self.printer, args=(self.text_STDOUT,))
        self.terminalThread.start()

        self.username = os.environ.get('USERNAME')

        # cmd_load_fw = [os.path.expanduser('~') + '/uhal101/pecond-sw/load_customFW.sh fw-2023Mar31']
        # cmd_load_fw = [os.path.expanduser('~') + '/uhal101/pecond-sw/load_customFW.sh active']
        # cmd_load_fw = ['/srv/hgcal/load_customFW_priv.sh']
        cmd_load_fw = ['sudo fw-loader load active']
        self.startFWload = tButton(self.window, "fw", 1, 8, self.queue, cmd_load_fw, shell=True)
        cmd_start_send = ["python3", os.path.expanduser('~') + '/uhal101/pecond-sw/zmqWorkArea/zmq_sendArray.py']
        self.SendLabc = tButton(self.window, "send to labc", 1, 9, self.queue, cmd_start_send)

    def on_exit(self):
        msg = "pressed exit button"
        self.queue.put(msg)
        self.StopTerminal.set()
        self.window.destroy()

    def printer(self, textbox=None):
        while not self.StopTerminal.is_set():
            data = self.queue.get()
            # some data comes in with the newline character and some doesn't
            # solution is to remove the newline if it exists and add a newline to all data
            print(data.replace('\n',''), flush=True, end="\n")
            textbox.insert(tk.END, data.replace('\n','') +'\n')
            textbox.see(tk.END)
            time.sleep(0.2)
            # self.queue.task_done()
        # self.queue.task_done()

    def cmd_loadfw(self):
        # os.system('source ~/uhal101/ROCv3/loadfw.sh')
        # os.system('/home/agrummer/uhal101/pecond-sw/load_customFW.sh fw-2023Feb18_longRun')
        # os.system('/home/agrummer/uhal101/pecond-sw/load_customFW.sh fw-2023Mar31')
        # os.system('./load_customFW.sh fw-2023Mar31')
        os.system('./load_customFW.sh active')

    def singlelinkWrite(self, Name, val, linkNum, block):
        block.getNode("link{0}.{1}".format(linkNum,Name)).write(int(val))
        self.hw.dispatch()

    def linksWrite(self, Name,val, numLinks, block):
        # numLinks=self.link_capture.getNode("global.num_links").read()
        # self.hw.dispatch()
        for i in range(numLinks):
            block.getNode("link{0}.{1}".format(i,Name)).write(int(val))
        self.hw.dispatch()

    def zcu_status(self):
       frontend=None
       fwback=self.backend.getNode("FIRMWARE_VERSION").read()
       if frontend is not None:
          fwfront=frontend.getNode("FIRMWARE_VERSION").read()
       st=self.backend.getNode("STATUS").read()
       er0=self.backend.getNode("LPGBT_ERROR_COUNTERS.LINK0").read()
       er1=self.backend.getNode("LPGBT_ERROR_COUNTERS.LINK1").read()
       er2=self.backend.getNode("LPGBT_ERROR_COUNTERS.LINK2").read()
       unlocks=self.backend.getNode("UNLOCK_COUNTER").read();
       rates=self.backend.getNode("RATES").readBlock(10+1+3)
       dlmodes=[]
       for i in range(0,4):
          dlmodes.append(self.backend.getNode("DOWNLINK_MODE%d"%(i)).read())
       ulmodes=[]
       if frontend is not None:
          for i in range(0,7):
             ulmodes.append(frontend.getNode("UPLINK_A.PATTERN%d"%(i)).read())
          ulmodes.append(frontend.getNode("UPLINK_B.PATTERN%d"%(0)).read())
          ulmodes.append(frontend.getNode("UPLINK_C.PATTERN%d"%(0)).read())
       self.hw.dispatch()
       if frontend is not None:
          self.queue.put(" Back FW %04x  Front FW %04x   Backend Status = %08x"%(fwback,fwfront,st))
       else:
          self.queue.put(" Back FW %04x  Backend Status = %08x"%(fwback,st))
       self.queue.put(" Errors (0,1,2) = %5d,%5d,%5d   Unlocks = %4d"%(er0,er1,er2,unlocks))

       rate_names=["100 MHz","Ref","TX","TX40","RX0","RX1","RX2","","RX0-DV","RX1-DV","RX2-DV","ERR0","ERR1","ERR2"]
       for irate in range(0,len(rates)):
          rate=rates[irate]
          if len(rate_names[irate])==0: continue
          if rate_names[irate][0:3]=="ERR":
             self.queue.put("  %10s: %.3f kHz"%(rate_names[irate],int(rate)*1e-1))
          else:
             self.queue.put("  %10s: %.8f MHz"%(rate_names[irate],(int(rate)*1e-4)))

       self.queue.put(" Downlink modes :")
       for i in range(0,4):
          self.queue.put("   EGROUP%d: (%x)"%(i,dlmodes[i]))

    def zcu_setrefclk(self):
       from smbus2 import SMBus, i2c_msg
       rates=self.backend.getNode("RATES").readBlock(10+1+3)

       # Arcane incantation to update Si570 clock rate
       # https://www.silabs.com/documents/public/data-sheets/si570.pdf
       refClkRate = rates[1]*1e-4

       hs_div_map = {0:4, 1:5, 2:6, 3:7, 5:9, 7:11}
       rev_hs_div_map = dict((reversed(item) for item in hs_div_map.items()))

       with SMBus(10) as bus:
          bus.write_byte(0x5d, 7, force=True)
          msg_read    = i2c_msg.read(0x5d, 6)

          bus.i2c_rdwr(msg_read)

       value = int.from_bytes(list(msg_read), byteorder="big", signed=False)

       rfreq = float(value&0x3fffffffff) / 2**28
       hs_div = hs_div_map[(value >> 45)&0x7]
       N1 = ((value >> 38)&0x7f) + 1

       fxtal = refClkRate * hs_div * N1 / rfreq

       newFreq = 320.64 #MHz

       # select HS_DIV and N1 such that 4.85 GHz < newFreq * HS_DIV * N1 < 5.67 GHz
       new_hs_div = 4
       new_N1 = 4

       new_rfreq = newFreq * new_hs_div * new_N1 / fxtal

       new_rfreq_int = int(new_rfreq * 2**28)

       i2c_data = [(rev_hs_div_map[new_hs_div] << 5) | (((new_N1-1) >> 2)&0x1f),
                   (((new_N1-1) << 6)&0xc0) | ((new_rfreq_int >> 32))&0x3f,
                   ((new_rfreq_int >> 24))&0xff,
                   ((new_rfreq_int >> 16))&0xff,
                   ((new_rfreq_int >> 8)) &0xff,
                   ((new_rfreq_int >> 0)) &0xff]

       with SMBus(10) as bus:
          bus.write_i2c_block_data(0x5d, 137, [0x18], force=True)
          bus.write_i2c_block_data(0x5d, 7, i2c_data, force=True)
          bus.write_i2c_block_data(0x5d, 137, [0x08], force=True)
          bus.write_i2c_block_data(0x5d, 135, [0x40], force=True)

    def zcu_resetlink(self):
       self.queue.put("Reseting the link")
       self.backend.getNode("CTL.GTH_RESET").write(1)
       self.backend.getNode("CTL.RX_RESET").write(1)
       status=self.backend.getNode("STATUS").read()
       self.hw.dispatch()
       self.queue.put(" Status = 0x%03x"%(int(status)))
       self.backend.getNode("CTL.GTH_RESET").write(0)
       self.backend.getNode("CTL.RX_RESET").write(0)

    def fc_rocd_reset(self):
    # ./uhal_string.py -b fc --node request.link_reset_rocd --val 1
    # ./uhal_string.py -b fc --node counters.link_reset_rocd
        self.fastcmd.getNode("request.link_reset_rocd").write(1)
        self.hw.dispatch()
        rocdresetval = self.fastcmd.getNode("counters.link_reset_rocd").read()
        self.hw.dispatch()
        self.labelrocdreset.config(text="ROCD resets: {}".format(rocdresetval))

    def fc_singleL1A(self):
    # ./uhal_string.py --b fc --node command.global_l1a_enable --val 1
    # ./uhal_string.py --b fc --node periodic0.request --val 1
    # ./uhal_string.py -b fc --node counters.l1a
    # ./uhal_string.py --b fc --node command.global_l1a_enable --val 0
        self.fastcmd.getNode("command.global_l1a_enable").write(1)
        self.hw.dispatch()
        self.fastcmd.getNode("periodic0.request").write(1)
        self.hw.dispatch()
        self.fastcmd.getNode("command.global_l1a_enable").write(0)
        self.hw.dispatch()
        l1aval = self.fastcmd.getNode("counters.l1a").read()
        self.hw.dispatch()
        self.labelL1A.config(text="L1As Sent: {}".format(l1aval))
        self.getStatus()

    def getStatusArrayLinks(self, Name, numLinks):
        # m = np.array([str(Name)])
        m = np.array([])
        for i in range(numLinks):
            val = self.link_capture.getNode("link{}.{}".format(i,Name)).read()
            self.hw.dispatch()
            m = np.append(m,int(val))
        return m

    def getStatus(self):
        for item in self.listBox.get_children():
           self.listBox.delete(item)
        numLinks=self.link_capture.getNode("global.num_links").read()
        self.hw.dispatch()
        headers = np.array(["link {}".format(x) for x in range(numLinks)], dtype=object)
        Name="link_enable"
        m = np.array([])
        for i in range(numLinks):
            val = self.link_capture.getNode("global.{}.link{}".format(Name,i)).read()
            self.hw.dispatch()
            m = np.append(m,int(val))
        m = np.stack((headers,m))
        for i,Name in enumerate(self.nNames):
            n2 = self.getStatusArrayLinks(Name,numLinks)
            m = np.concatenate((m,[n2]))
        tableNames = np.insert(self.nNames, 0, "link_enable")
        tableNames = np.insert(tableNames, 0, "namesheader")
        self.listBox.tag_configure('pass', background='lightgreen', font=('Courier',13,'normal'))
        self.listBox.tag_configure('fail', background='PaleVioletRed', font=('Courier',13,'normal'))
        self.listBox.tag_configure('neutral', font=('Courier',13,'normal'))
        for i in range(1, m.shape[0]):
            if i==5 and m[i][2]==m[i][4]==m[i][5]==128.: my_tag='pass'
            elif i==5: my_tag='fail'
            elif i==8 and np.all(m[i]==1.): my_tag='pass'
            else: my_tag = 'neutral'
            self.listBox.insert("", "end",text = tableNames[i], values=tuple(m[i]), tags=(my_tag))

    def readFIFO(self):
        for item in self.listBox.get_children():
           self.listBox.delete(item)
        numLinks=self.link_capture.getNode("global.num_links").read()
        self.hw.dispatch()
        headers = np.array(["link {}".format(x) for x in range(numLinks)], dtype=object)
        bLength=[self.link_capture.getNode("link{0}.fifo_occupancy".format(i)).read() for i in range(numLinks)]
        self.hw.dispatch()
        maxLength = max(bLength)
        for i in range(numLinks):
            if i==0:
                if bLength[i] == 0:
                    vecval = np.empty((maxLength,1))
                    vecval[:] = np.NaN
                    continue
                vecval = self.link_capture_fifo.getNode("link{0}".format(i)).readBlock(int(bLength[i]))
                self.hw.dispatch()
                # vecval=[hex(x)[2:] for x in vecval]
                vecval=["{:08x}".format(x) for x in vecval]
            else:
                if bLength[i] == 0:
                    vecval2 = np.empty((maxLength,1))
                    vecval2[:] = np.NaN
                    vecval=np.column_stack((vecval,vecval2))
                    continue
                vecval2 = self.link_capture_fifo.getNode("link{0}".format(i)).readBlock(int(bLength[i]))
                self.hw.dispatch()
                # vecval2=[hex(x)[2:]for x in vecval2]
                vecval2=["{:08x}".format(x) for x in vecval2]
                vecval=np.column_stack((vecval,vecval2))
        for i in range(0, vecval.shape[0]):
            self.listBox.insert("", "end",text = "{}".format(i), values=tuple(vecval[i]))
    #      table = tabulate(vecval,headers,showindex=True, tablefmt="simple")
    #      print(table)
    # table = tabulate(m, tablefmt="simple",headers="firstrow")
    # print(table)

    def lc_resetaqcuire(self):
        numLinks=self.link_capture.getNode("global.num_links").read()
        self.hw.dispatch()
        self.linksWrite("aquire_length", 0, numLinks, self.link_capture)
        self.linksWrite("capture_mode_in", 0, numLinks, self.link_capture)
        self.linksWrite("L1A_offset_or_BX", 0, numLinks, self.link_capture)
        self.link_capture.getNode("global.continous_acquire").write(int(0))
        self.hw.dispatch()
        self.linksWrite("explicit_rstb_acquire", 0, numLinks, self.link_capture)
        self.getStatus()
        self.ConfigButton.configure(bg = "#6F8FAF", activebackground="#6F8FAF", command = self.ConfigCommands)

    def ConfigCommands(self):
        # label = tk.Label(self.window, text="psuedo Econ D Status" ).grid(row=4, columnspan=3)
        # self.linksWrite(Name,val, numLinks, block):
        numLinks=self.link_capture.getNode("global.num_links").read()
        self.hw.dispatch()
        # self.linksWrite("align_pattern", 2899102912, numLinks, self.link_capture)
        self.linksWrite("align_pattern", 2899102924, numLinks, self.link_capture)
        # self.linksWrite("align_pattern", 3435973836, numLinks, self.link_capture)
        self.link_capture.getNode("global.explicit_align").write(int(1))
        self.hw.dispatch()
        # self.linksWrite("L1A_offset_or_BX", 31, numLinks, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link0Offset.get(), 0, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link1Offset.get(), 1, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link2Offset.get(), 2, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link3Offset.get(), 3, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link4Offset.get(), 4, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link5Offset.get(), 5, self.link_capture)
        self.singlelinkWrite("L1A_offset_or_BX", self.var_Link6Offset.get(), 6, self.link_capture)
        if self.lpgbt == "trig":
            self.singlelinkWrite("L1A_offset_or_BX", self.var_Link3Offset.get(), 10, self.link_capture)
            self.singlelinkWrite("L1A_offset_or_BX", self.var_Link4Offset.get(), 11, self.link_capture)
            self.singlelinkWrite("L1A_offset_or_BX", self.var_Link5Offset.get(), 12, self.link_capture)
            self.singlelinkWrite("L1A_offset_or_BX", self.var_Link6Offset.get(), 13, self.link_capture)

        self.linksWrite("aquire_length", self.var_CapLen.get(), numLinks, self.link_capture)
        self.linksWrite("capture_mode_in", 2, numLinks, self.link_capture)
        self.link_capture.getNode("global.continous_acquire").write(int(63))
        self.hw.dispatch()
        self.getStatus()
    # 7 ./uhal_string.py --links align_pattern --val 2899102912
    # 6 ./uhal_string.py --links align_pattern --myhex
    # 5 ./uhal_string.py --node global.explicit_align --val 1
    # 4 ./uhal_string.py --links L1A_offset_or_BX --val 31
    # 3 
    # 2 ./uhal_string.py --links aquire_length --val 500
    # 1 ./uhal_string.py --links capture_mode_in --val 2
    # 8   ./uhal_string.py --node global.continous_acquire --val 63
        self.btn_text.set("Configured")
        self.ConfigButton.configure(bg = "#AFF8DB", activebackground="#AFF8DB", command = None)

    def ApplyNewVal(self, name, value):
        self.queue.put(name, value)

    def OnDoubleClick(self, event):
        item = self.listBox.selection()
        # print('item:', item)
        # print('event:', event)
        item = self.listBox.selection()[0]

        newWindow = tk.Toplevel(self.window)
        # Toplevel widget
        newWindow.title("New Window")
        # sets the geometry of toplevel
        #newWindow.geometry("400x200")

        newVal = tk.IntVar()

        def exit_btn():
            newWindow.destroy()
            newWindow.update()

        tk.Label(newWindow, text =self.listBox.item(item,"text")).grid(row=1, column=0, columnspan=2, sticky="NSEW")
        w = tk.Scale(newWindow, from_=1, to=0, orient=tk.HORIZONTAL, variable =newVal ).grid(row=2, column=1, sticky="NSEW")
        # A Label widget to show in toplevel
        NWapplyButton = tk.Button(newWindow, text="Apply", width=15, command=lambda: self.ApplyNewVal(self.listBox.item(item,"text"),newVal.get())).grid(row=4, column=0, sticky="NSEW")
        NWcloseButton = tk.Button(newWindow, text="Close", width=15, command=exit_btn).grid(row=4, column=1, sticky="NSEW")
        # newWindow.attributes('-topmost', True)
        # newWindow.lift()
        newWindow.transient(self.window) # set to be on top of the main window
        newWindow.wait_visibility()
        newWindow.grab_set() # hijack all commands from the master (clicks on the main window are ignored)
        self.window.wait_window(newWindow) # pause anything on the main window until this one closes

        # print("you clicked on", self.listBox.item(item,"text"))

 

def main():
    window = tk.Tk() 
    window.title("Main Window")
    window.geometry("800x600")

    gui = CoreGUI(window)
    window.mainloop()

if __name__ == '__main__':
    main()
