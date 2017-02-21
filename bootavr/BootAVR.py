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

class BootAVRException(Exception):
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
        # set verbose to False to disable printing of progress messages etc
        self.verbose=True

    def printer(self, msg="", eol=True):
        """ print the passed sting but on if self.verbose is set to True """
        if(self.verbose):
            if eol:
                print msg
            else:
                print msg,
            sys.stdout.flush()


    def handleMsg(self, msg):
        """ """
        # add message to queue
        self.rxq.put(msg);


    def getVersion(self, warn=True):
        """ """
        msg=self.sendReceive(self.CMD_VERSION_READ, warn=warn);
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


    def sendReceive(self, msgs, timeoutSec = 1, warn=True):
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
            if warn:
                logging.warn("sendReceive() receive timeout");
            rmsg=None
        return rmsg;


    def dumpFlash(self, filename):
        """Reads the contents of MCU's entire flash memory and dumps to specified file"""
        self.printer("Reading flash...");
        self.initMemory();
        self._mcuRead(eeprom=False);
        self.memory.dumpToFile(filename);


    def dumpEEPROM(self, filename):
        """Reads the contents of MCU's entire EEPROM memory and dumps to specified file"""
        self.printer("Reading EEPROM...");
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


    def _mcuRead(self, eeprom=False):
        """Read the entire flash/eeprom from the MCU into the memory.
           Memory should have been initialised prior.
        """
        mem='flash';
        if(eeprom):
            mem='eeprom'
            self.printer("Reading {}...\r".format(mem));
        # work out page number of last page
        maxPage=self.bootPage;
        if eeprom:
            maxPage=int(self.eepromSize/self.pageSizeBytes);

        for pageNum in range(0, maxPage):
            # loop thru each page by page-number.
            self.printer("page: {}{}".format(pageNum,"\r"), False)

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

        self.printer("\nDone.");


    def eepromErase(self):
        """ Erase the entire EEPROM. note: EEPROM is erage by writing 0xFF to every byte"""
        self.printer("Erasing EEPROM...")
        # byte array, one page in size, set to all 0xFFs
        m = Memory(self.pageSizeBytes);
        # erase eeprom, one page at a time.
        for a in range(0, self.eepromSize, self.pageSizeBytes):
            self.printer("Page: 0x{:02x}{}".format( a/self.pageSizeBytes, "\r"), False)
            self.writeEEPROM(a, m.memory);
        self.printer("")
        self.printer("Done.")


    def writeEEPROM(self, addr, dataByteA):
        """
        The size of the data that can be written is limited by the maximum message size.
        """
        m=pack('<cHB',self.CMD_EEPROM_WRITE, addr, len(dataByteA));
        m+=str(dataByteA);
        msg=self.sendReceive(m);
        # potential error message
        em=""
        # no response message was received
        if msg == None:
            em="no response from MCU"
        # check response message
        if not msg.len == 1:
            em = "response from MCU was invalid"
        if not msg.data[0] == 1:
            em = "MCU indicated that write failed at or near address: {}".format(addr)
        if not em == "":
            raise BootAVRException(em);


    def flashErase(self):
        """Erase the mcu's entire FLASH, excluding the boot section."""
        self.printer("Erasing Flash...", False)
        for pn in range(0, self.bootPage):
            self.flashErasePage(pn);
        self.printer("")
        self.printer("Done.")


    def flashErasePage(self,pageNum):
        """ """
        m=pack('<cB', self.CMD_FLASH_ERASE, pageNum);
        msg=self.sendReceive(m);
        # potential error message
        em=""
        # no response message was received
        if msg == None:
            em="no response from MCU"
        # check response message
        if not msg.len == 1:
            em = "response from MCU was invalid"
        if not msg.data[0] == 1:
            em = "MCU indicated that erase failed"
        if not em=="":
            raise BootAVRException(em);


    def flashPageWrite(self, pageNum, dataByteA):
        """"""
        m=pack('<cB', self.CMD_FLASH_WRITE, pageNum);
        m+=str(dataByteA);
        msg=self.sendReceive(m);
        # no response message was received
        if msg == None:
            em="no response from MCU"
        # check response message
        em=""
        if not msg.len == 1:
            em = "response from MCU was invalid"
        if not msg.data[0] == 1:
            em = "MCU indicated that erase failed, page: {}".format(pageNum)
        if not em=="":
            raise BootAVRException(em);


    def _mcuWrite(self, verify=True, eeprom=False):
        """
        Write contents of the memory to flash or to eeprom.
        Parameters:
          * eeprom if true, write to eeprom, if false(default) write to flash
        Return: False if verify fails, True otherwise
        """

        # This is the value that is returned, assume success
        returnValue=True;

        # Keep a copy of the pages that are actually written (ie non-blank) for later verification
        writtenPages={};

        mem='flash';
        if(eeprom):
            mem='eeprom'

        self.printer("Writing {}...".format(mem))
        # work out page number of last page
        maxPage=self.bootPage;
        if eeprom:
            maxPage=int(self.eepromSize/self.pageSizeBytes);
        for pageNum in range(0, maxPage):
            # loop thru each page by page number.
            if(not self.memory.isPageBlank(pageNum)):
                # page contains data, write it to flash/eeprom
                self.printer("page: {}{}".format(pageNum,"\r"), False)
                page= bytearray();
                page = self.memory.getPage(pageNum);
                if(eeprom):
                    # write to eeprom.
                    self.writeEEPROM(self._pageNumToAddr(pageNum), page);
                else:
                    # write to flash
                    self.flashPageWrite(pageNum, page);
                writtenPages[pageNum]=page;
#        self.printer("");
        
        if(verify):
            self.printer("Verifying {}...".format(mem))
            for pageNum in range(0, self.bootPage):
                if writtenPages.has_key(pageNum):
                    self.printer("page: {}\r".format(pageNum), False)
                    # convert page number to address
                    addr=pageNum * self.pageSizeBytes
                    if(eeprom):
                        # verifying eeprom
                        fePage=self.readEEPROM(addr,self.pageSizeBytes).data;
                    else:
                        # verifying flash
                        fePage=self.flashRead(addr, self.pageSizeBytes).data;
                    # XXX yeah, yeah, copy, copy ...
                    ourPage=writtenPages[pageNum]; 
                    for b in range(0, self.pageSizeBytes):
                        if(ourPage[b] != fePage[b]):
                           em="Verification of page: 0x{:02x} failed.".format(pageNum)
                           logging.error(em);
                           self.printer(em)
                           returnValue=False;
            self.printer();
        return returnValue;


    def flashWriteFile(self, filename,  flashAddr=0):
        """ """
        self.printer("Preparing to write file to flash.".format(filename))
        if not flashAddr ==0 :
            self.printer("Starting at address: 0x{:02x}".format(str(flashAddr)));
            self.printer("Reading binary file: {}".format(filename))
        self.initMemory();
        self.memory.loadBinFile(filename, flashAddr);
        r=self._mcuWrite(verify=True, eeprom=False)
        if r:
            self.printer("Success.");
            return True;
        else:
            self.printer("Failed.")
            return False;

            
    def eepromWriteFile(self, filename,  eepromAddr=0):

        """ """
        self.printer("Preparing to write file to EEPROM.".format(filename))
        if not eepromAddr ==0 :
            self.printer("Starting at address: 0x{:02x}".format(str(eepromAddr)));
            self.printer("Reading binary file: {}".format(filename))
        self.initMemory();
        self.memory.loadBinFile(filename, eepromAddr);
        r=self._mcuWrite(verify=True, eeprom=True)
        if r:
            self.printer("Success.");
            return True;
        else:
            self.printer("Failed.")
            return False;


    def _pageNumToAddr(self, pn):
        """Convert passed page number to memory address"""
        return int(pn * self.pageSizeBytes);
