# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2017. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys, os, threading, time, binascii, traceback, logging
import Queue;
from struct import * ;
from Transport import Transport


class MMPMsg:
    """ """
    def __init__(self):
        """ """
        self.data=bytearray();
        # expected length of the message
        self.len=0;
        # count of the number of data bytes received so far
        self.count=0;


# -------------------------------------------        
class MMP:
    """ """
    # byte indicating start of message
    MSG_SOM='S'
    MSG_STX='T'
    MSG_ETX='E'

    # string used to match logger strings
    LOGS = '	LOG'
    # max length of log string
    LOGS_MAX = 255;

    def __init__(self, transport=None):
        """ """
        self.reader = threading.Thread(target=self.readerThread)
        self.reader.start();
        self.alive= True
        self.transport=transport
        if transport == None:
            # use default transport
            logging.warn("MMP is using default transport")
            self.transport=Transport()
        pass

    def handleMsg(msg):
        """ """
        print "MSG! "+msg

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
        print "nh: {:s}".format(byte);


    def logStrReceived(self, logStr):
        """ """
        # don't print leading \t
        logging.info("MCU: "+logStr[1:])


    def calcCS(self, intCS):
        return (256 - intCS) %256


    def handleMsg(self, msg):
        logging.info("PC RX: len: {}, data: {}".format(msg.len, msg.data));
        #print "Data as hex:"
        #print ''.join("-0x"+format(b, '02x') for b in msg.data)
        # if(ord(c)!=0):
        #     print c;
        # print '0x{:x}'.format(ord(c))


    def sendMsg(self, msgData):
        """ """
        length = len(msgData)
        # make up  header
        # checksum
        cs=length;
        m=pack('<cBc', self.MSG_SOM, length, self.MSG_STX);
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
        
        logi = 0;
        state = SIDLE;
        logstr = '';
        msg = MMPMsg();
        # checksum
        cs = 0;

        try:
            while self.alive:
                c = self.readByte();
                if(c != None and len(c) != 0):
                    # char (python string) has been received,
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
                            self.logStrReceived(logstr)
                            state = SIDLE
                            logstr = '';
                        else:
                            logstr = logstr + c;
                            if len(logstr) > self.LOGS_MAX:
                                logging.warn("log string is too long. Truncated: "+logstr+"\n")
                                self.logStrReceived(logstr)
                                state = SIDLE
                                logstr = '';
                    # ---------------------------------
                    elif state == SLEN:
                        # recived char is message length
                        msg.len = ord(c)
                        cs = msg.len
                        logging.debug("-LEN-")
                        state = SSTX

                    elif state == SSTX:
                        if (c == self.MSG_STX):
                            # got STX char as expected
                            logging.debug("-STX-")
                            state = SDATA
                        else:
                            # did not get SSTX char when expected
                            logging.debug("!STX not seen!")
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
                            logging.debug("!ETX not seen!")

                    elif state == SCS:
                        if ord(c) == self.calcCS(cs):
                            # checksum was valid, message is complete
                            self.handleMsg(msg)
                        else:
                            # checksum was invalid
                            logging.debug("!invalid checksum, expected: 0x{:x} got 0x{:x}".format(self.calcCS(cs), ord(c)))
                        state = SIDLE

                else:
                    # timeout: no byte received
                    if state != SIDLE:
                        logging.debug("timeout")
                        state = SIDLE
                    pass


                
        except Exception, e:
            logging.error("Caught exception in reader thread: {}".format(e))
#            traceback.print_exc(e)
#            raise e
        return




    