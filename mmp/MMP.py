# ------------------------------------------------------------------------------
# Copyright 2020 Stephen Stebbing. telecnatron.com
#
#    Licensed under the Telecnatron License, Version 1.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://telecnatron.com/software/licenses/
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ------------------------------------------------------------------------------
import sys, os, threading, time, binascii, traceback, logging
from struct import * ;
from Transport import Transport


class MMPMsg:
    """ Class represents a MMP message"""
    def __init__(self):
        """ """
        self.data=bytearray();
        # expected length of the message/ lenght of the received message, 1 byte
        self.len=0;
        # flags, 1 byte
        self.flags=0;
        # count of the number of data bytes received so far
        self.count=0;

    def __str__(self):
        s="data length: {}, ".format(self.len)
        s = s+ "flags: 0x{:02x}, ".format(self.flags)
        s = s + "data: "
        for ch in self.data:
            s = s + "0x{:x},".format(ch)
        s = s+ " str: "
        for ch in self.data:
            s = s + "{}".format(chr(ch))
        return s

       

# -------------------------------------------        
class MMP:
    """ """
    # byte indicating start of message
    MSG_SOM='\1'
    MSG_STX='\2'
    MSG_ETX='\3'

    # string used to match logger strings
    LOGS = '	LOG'
    # max length of log string
    LOGS_MAX = 255;

    def __init__(self, transport=None):
        """ """
        self.alive= True
        self.transport=transport
        # Default message flags byte, used if None is specified in method calls
        self.flags=0
        if transport == None:
            # use default transport
            logging.warn("MMP is using default transport")
            self.transport=Transport()
        # keep track of how many errors have occured
        self.errors_rx = 0
        self.errors_timeout = 0
        self.errors_log = 0;
        # keep track of how many messages and log strings have been received
        self.num_log = 0;
        self.num_msg = 0;
        # init reader thread
        self.reader = threading.Thread(target=self.readerThread)
        self.reader.start();


    def stop(self):
        """ """
        self.alive=False


    def readByte(self):
        """ """
        return self.transport.readByte();


    def write(self, databytes):
        """ """
        self.transport.write(databytes);


    def nonHandledByte(self, byte):
        """ """
        #print "nh: {:s}".format(byte);
        pass


    def logStrReceived(self, logStr):
        """ """
        # don't print leading \t
        logging.info("MCU: "+logStr[1:])


    def calcCS(self, intCS):
        return (256 - intCS) %256


    def handleMsg(self, msg):
        """ Called when a message is received. Expected to be overriden in subclasses. """
        logging.info("PC RX: {}".format(msg));


    def rebootMCU(self):
        """ Send MCU message telling it to reboot itself."""
        self.sendMsg('r',flags=0x0)

    def sendMsg(self,  msgData, flags=None):
        """ """
        # use default flags if not specified as parameter
        if flags == None:
            flags=self.flags;

        length = len(msgData)
        # make up  header
        # checksum
        cs=length+flags;
        m=pack('<cBBc', self.MSG_SOM, length, flags, self.MSG_STX);
        # add data
        for ch in msgData:
            m += pack('<c',ch);
            cs += ord(ch)
            cs = cs % 256
        # pack ETX
        m += pack('<c', self.MSG_ETX)
        # pack CS
#        m += pack('<B', self.calcCS(cs));
        m += pack('<B', cs);
        self.write(m)


    def readerThread(self):
        """ """
        # states
        SIDLE  = 0
        SLOG   = 1
        SSTX   = 2
        SDATA  = 3
        SETX   = 4
        SLEN   = 5
        SCS    = 6
        SFLAGS = 7
        
        logi = 0;
        state = SIDLE;
        logstr = '';
        msg = MMPMsg();
        # checksum
        cs = 0;
        while self.alive:
            try:
                c = self.readByte();
                if(c != None and len(c) != 0):
                    # char (python string) has been received,
                    #if ( ord(c) >= 32 and ord(c)<=127):
                    #    a=c;
                    #else:
                    #    a='_'
                    #s="~0x{:02x}={}".format(ord(c),a);
                    #print s,
                    
                    # ---------------------------------
                    if state == SIDLE:
                        if c == self.MSG_SOM:
                            # got start byte
                            logi = 0
                            state = SLEN
                            msg = MMPMsg();
                            logging.debug("-SOM-")
                        else:
                            if c == self.LOGS[logi]:
                                # got a LOGS char
                                logi += 1
                                if logi == len(self.LOGS):
                                    # Yup, this is a LOG string
                                    logstr=self.LOGS;
                                    state = SLOG
                                    logi=0;
                            else:
                                # nope, false alarm, char received was not start of message, not start of log string
                                logi=0;
                                self.nonHandledByte(c)
                    # ---------------------------------
                    elif state == SLOG:
                        # we're receiving a log msg
                        if c == '\n':
                            # this is end of log string
                            self.num_log += 1
                            self.logStrReceived(logstr)
                            state = SIDLE
                            logstr = '';
                        else:
                            logstr = logstr + c;
                            if len(logstr) > self.LOGS_MAX:
                                logging.warn("log string is too long. Truncated: "+logstr+"\n")
                                self.errors_log += 1;
                                self.logStrReceived(logstr)
                                state = SIDLE
                                logstr = '';
                    # ---------------------------------
                    elif state == SLEN:
                        # recived char is message length
                        msg.len = ord(c)
                        cs = msg.len 
                        logging.debug("-LEN-")
                        state = SFLAGS

                    elif state == SFLAGS:
                        # recived char is message length
                        msg.flags = ord(c)
                        cs += ord(c) 
                        logging.debug("-FLAGS-")
                        state = SSTX

                    elif state == SSTX:
                        if (c == self.MSG_STX):
                            # got STX char as expected
                            logging.debug("-STX-")
                            state = SDATA
                        else:
                            # did not get SSTX char when expected
                            logging.debug("!STX not seen!")
                            self.errors_rx += 1
                            state = SIDLE
                    elif state == SDATA:
                        # we're receiving msg data.
                        # XXX note: msg must contain at least one byte of data, ie no zero sized data is allowed here
                        msg.data.extend(c);
                        #logging.debug("d:"+c)
                        cs += ord(c)
                        msg.count += 1
                        if msg.count == msg.len:
                            # that was the last of the data
                            state = SETX

                    elif state == SETX:
                        if( c == self.MSG_ETX ):
                            # got ETX char as expected.
                            logging.debug("-ETX-")
                            state = SCS
                        else:
                            # did not get ETX char as expected
                            self.errors_rx += 1
                            logging.debug("!ETX not seen!")

                    elif state == SCS:
                        if ord(c) == self.calcCS(cs) :
                            # checksum was valid, message is complete
                            self.num_msg += 1
                            self.handleMsg(msg)
                        else:
                            # checksum was invalid
                            self.errors_rx += 1
                            logging.debug("!invalid checksum, expected: 0x{:x} got 0x{:x}".format(self.calcCS(cs), ord(c)))
                        state = SIDLE

                else:
                    # timeout: no byte received
                    if state != SIDLE:
                        logging.debug("timeout")
                        self.errors_timeout += 1
                        state = SIDLE
                    pass

            except Exception, e:
                logging.error("Caught exception in reader thread: {}".format(e))
                #            traceback.print_exc(e)






    
