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
from Memory import Memory

class BootAVRException:
    """Exception thrown by BootAVR on certain errors"""
    pass


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
        # MCU info as retreived by getVersion()
        self.version="";
        self.signature="";
        self.mcu="";
        self.bootPage=0;
        self.bootAddress=0;
        self.eepromSize=0;
        self.pageSizeBytes=0;
        self.memory=();


    def handleMsg(self, msg):
        """ """
        # add message to queue
        self.rxq.put(msg);


    def getVersion(self):
        """ """
        msg=self.sendReceive(self.CMD_VERSION_READ);
        if not msg == None:
            # Extract data from response.
            if msg.data[0] == ord(self.CMD_VERSION_READ):
                # next 3 bytes are the mcu id signature
                sig = msg.data[1:4]
                sigstr=""
                for ch in sig:
                    sigstr = sigstr +"{:02x}".format(ch).upper();
                # next byte is the bootloader start page
                spage = msg.data[4]
                # we return a dictionary,
                vers="".join(map(chr, msg.data[5:]))
                mcui=self.sigs.getMCUInfo(sigstr)
                mcui["bootStartPage"]=spage;
                dict= {
                    "mcu_info":  mcui,
                    "version":   vers,
                    "signature": sigstr,
                };
                self.version=vers
                self.signature=sigstr
                self.mcu=mcui["name"]
                # get bootloader-start page from mcu
                self.bootPage = spage
                # starting address of bootloader from mcu
                self.bootAddress=self.bootPage * mcui['pageSizeBytes'];
                self.eepromSize=mcui["eepromSizeBytes"]
                self.pageSizeBytes=mcui["pageSizeBytes"]
                return dict;
        # no or invalid response
        return None


    def runApp(self):
        """ """
        msg=self.sendReceive(self.CMD_RUN_APPLICATION)
        if not msg == None:
            if msg.len == 1 and chr(msg.data[0]) == self.CMD_RUN_APPLICATION:
                return True
        return False;


    def sendReceive(self, msgs, timeoutSec = 1):
        """ """
        # flush rx queue
        while not self.rxq.empty():
            self.rxq.get_nowait();
        # send msg
        self.sendMsg(msgs);
        # wait for response
        try:
            rmsg= self.rxq.get(True, timeoutSec)
        except Queue.Empty, e:
            logging.warn("sendReceive() receive timeout");
            rmsg=None
        return rmsg;


    def dumpFlash(self, filename):
        """Reads the contents of MCU's entire flash memory and dumps to specified file"""
        self.initMemory();
        self._mcuRead(eeprom=False);
        self.memory.dumpToFile(filename);


    def dumpEEPROM(self, filename):
        """Reads the contents of MCU's entire EEPROM memory and dumps to specified file"""
        self.initMemoryEEPROM();
        self._mcuRead(eeprom=True);
        self.memory.dumpToFile(filename);



    def initMemory(self, size=0, pageSize=0):
        """ Initialise a new memory object set it's size to that of the MCU's flash memory"""
        if(size==0):
            size=self.bootAddress;
        if(pageSize==0):
            pageSize=self.pageSizeBytes;
        self.memory=Memory(size, self.pageSizeBytes);
        return self.memory;


    def initMemoryEEPROM(self):
        """ Initialise a new memory object set it's size to that of the MCU's EEPROM memory """
        self.memory=Memory(self.eepromSize, self.pageSizeBytes);
        return self.memory;


    def readEEPROM(self, addr, length):
        """
        Returns: object of class Msg (Msg.data being the read data) or None if read failed.
        """
        msgs=pack('<cHB',self.CMD_EEPROM_READ,addr,length)
        return self.sendReceive(msgs);
    

    def flashRead(self, addr, length):
        """
        Returns: object of class Msg (Msg.data being the read data) or None if read failed.
        """
        msgs=pack('<cHB',self.CMD_FLASH_READ,addr,length);
        return self.sendReceive(msgs)


    def _mcuRead(self, eeprom=False, verbose=True):
        """Read the entire flash/eeprom from the MCU into the memory.
           Memory should have been initialised prior.
        """
        mem='flash';
        if(eeprom):
            mem='eeprom'
        if verbose:
            print "Reading ", mem, "... ";
        # work out page number of last page
        maxPage=self.bootPage;
        if eeprom:
            maxPage=int(self.eepromSize/self.pageSizeBytes);

        for pageNum in range(0, maxPage):
            # loop thru each page by page-number.
            if verbose:
                print "page: ",pageNum,"\r",
                sys.stdout.flush()

            # convert page number to address
            addr=pageNum * self.pageSizeBytes
            if(eeprom):
                # read eeprom page
                fePage=self.readEEPROM(addr,self.pageSizeBytes).data;
            else:
                # read flash page
                fePage=self.flashRead(addr, self.pageSizeBytes).data;

            if fePage == None:
                logging.error("Read failed");
                raise BootAVRException("Read failed");

            self.memory.set(addr, fePage);

        if verbose:
            print "Done:";
        





