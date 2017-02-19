# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2017. http://telecnatron.com/
# -----------------------------------------------------------------------------
#/**
# * @file   BootAVR.py
# * @author steves
# * @date   2017/02/19 08:44:59
# * 
# * @brief  
# * 
# */
import sys, os, time, binascii, traceback, logging
import Queue;
from struct import * ;
from telecnatron import mmp
from ATmegaSignatures import ATmegaSignatures

class BootAVR(mmp.MMP):
    """ """

    # Characters signifying the various commands that get
    # send to the MCU
    CMD_EEPROM_READ    = 'e';
    CMD_EEPROM_WRITE   = 'E';
    CMD_FLASH_ERASE    = 'C';
    CMD_FLASH_READ     = 'f';
    CMD_FLASH_WRITE    = 'F';
    CMD_RUN_APPLICATION= 'R';
    CMD_VERSION_READ   = 'V';

    
    def __init__(self, port, baud, timeoutSec = 0.1):
        """ """
        mmp.MMP.__init__(self, mmp.SerialTransport(port, baud, timeoutSec) );
        # dictionary of MCU signature to device names.
        self.sigs=ATmegaSignatures();
        # Queue object holds received messages
        self.rxq = Queue.Queue(maxsize=1);
        # queue for received messages


    def handleMsg(self, msg):
        """ """
        # add message to queue
        self.rxq.put(msg);


    def getVersion(self):
        """ """
        msg=self.sendReceive(self.CMD_VERSION_READ);
        print msg
        if not msg == None:
            # Extract data from response.
            if msg.data[0] == ord(self.CMD_VERSION_READ):
                # next 3 bytes are the mcu id signature
                sig = msg.data[1:4]

                sigstr=""
                for ch in sig:
                    sigstr = sigstr +"{:02x}".format(ch).upper();
                

                print sigstr

                print self.sigs.getMCUInfo(sigstr);
                # remaining bytes are the version string
                ver = msg.data[4:]
                print "version: "+ver


        # no or invalid response
        return None


    def sendReceive(self, msg, timeoutSec = 1):
        """ """
        # flush rx queue
        while not self.rxq.empty():
            self.rxq.get_nowait();
        # send msg
        self.sendMsg(msg);
        # wait for response
        try:
            rmsg= self.rxq.get(True, timeoutSec)
        except Queue.Empty, e:
            logging.warn("sendReceive() receive timeout");
            rmsg=None
        return rmsg;







