# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2017. http://telecnatron.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# -----------------------------------------------------------------------------
import sys, os, threading, time, binascii, traceback, logging
from struct import * ;
from Transport import Transport

""" MMP: Microcontroller Message Protocol: a very simple communications protocol for microcontrollers
This package provides for coms between a PC and a MCU via a RS232 serial for example."
""" 

class MMPMsg:
    """ Class represents a MMP message"""
    def __init__(self):
        """Initialise the object"""
        self.data=bytearray();
        # expected length of the message/ lenght of the received message, 1 byte
        self.len=0;
        # flags, 1 byte
        self.flags=0;
        # count of the number of data bytes received so far
        self.count=0;

    def __str__(self):
        """ return string representation of the object. """
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

    # Bytes indicating significance in a message that is being received:
    # start of message
    MSG_SOM='\1'
    # start of text
    MSG_STX='\2'
    # end of text
    MSG_ETX='\3'

    # string used to match start of logger strings, note that log strings are terminiated with '\n'
    LOGS = '	LOG'
    # max length of log string
    LOGS_MAX = 255;

    def __init__(self, transport=None):
        """
        :param transport: (Reference to) object of class mmp.Transport that is used to send and receive bytes on the communications channel.
        """
        # thread reads incoming data from Transport
        self.reader = threading.Thread(target=self.readerThread)
        self.reader.start();
        # flag used to indicate to reader thread should continue or exit.
        self.alive= True
        # Default message flags byte, used if None is specified in method calls
        self.flags=0
        self.transport=transport
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


    def stop(self):
        """ Stop reading from Transport, shut down."""
        self.alive=False


    def readByte(self):
        """see Transport.readByte()"""
        return self.transport.readByte();


    def write(self, databytes):
        """:see: Transport.write()"""
        self.transport.write(databytes);


    def nonHandledByte(self, byte):
        """ 
        Called when a byte has been received that is not part of a message or a log message.
        :param byte: The byte (char or whatever it is in python)

        """
        #print "nh: {:s}".format(byte);
        pass


    def logStrReceived(self, logStr):
        """Called when a log string has been received. Prints string using logging.info(). 
        Expected to be overriden in subclasses.
        :param logStr: The received log string
        """

        # don't print leading \t
        logging.info("MCU: "+logStr[1:])


    def calcCS(self, intCS):
        """Convert passed sum to message checksum
        :param intCS: Sum of the checksumable chars in current received message
        :type intCS: unsigned integer
        :returns: The checksum that should match the checksum received in the message
        :rtype: integer ( modded to 8 bits)

        """
        return (256 - intCS) %256


    def handleMsg(self, msg):
        """Called when a message has been received. Logs the message as string.
        Expected to be overriden in subclass.
        :param msg: Object representing the received message.
        :type msg: mmp.Msg
        """
        logging.info("PC RX: {}".format(msg));


    def rebootMCU(self):
        """ Send MCU message telling it to reboot itself."""
        self.sendMsg('r',flags=0x0)

    def sendMsg(self,  msgData, flags=None):
        """Send the passed data as a message.
        :param msgData: The data for the message to be sent. May be string or bytearray.
        :param flags: The flags field for the message. Used by higher level protocol and 
        not of significance here. If None, the default value of self.flags (currently =0) is used.
        """
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
        """Thread-loop method that is called by self.reader thread:
        * Polls for and implements the protocol for received messages and log strings.
        * Calls the callback methods handleMessage(), logStringReceived() and nonHandlerByte() as required.
        * Set self.alive to have the thread exit at completion of current loop.
        """
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






    
