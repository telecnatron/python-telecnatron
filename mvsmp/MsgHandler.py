# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import os
import serial
import threading
import binascii
import traceback
import logging
import Queue
#from struct import * 
from Msg import Msg

# -------------------------------------------        
class MsgHandler:
    """ """

    # max size of msg received queue
    RX_QUEUE_MAX  = 8;
    # string used to match logger strings
    LOGS = '|LOG'
    # max length of log string
    LOGS_MAX = 120;
    # Max num of log messages in log queue
    LOG_QUEUE_MAX = 16

    def __init__(self, port, baud, timeoutSec=2):
        """ """
        try:
            # create serial port object, open port
            self.serial = serial.Serial(port, baud, timeout=timeoutSec);
        except Exception, e:
            sys.stderr.write("Could not open serial port %s: %s\n" % (port, e))
            raise e;
        # Queue object holds received messages
        self.rxq = Queue.Queue(maxsize=self.RX_QUEUE_MAX);
        self.alive = True
        self.reader = threading.Thread(target=self.reader_thread)
        """Set debug to True to have messages printed to screen on sending and receipt."""
        self.debug=False;
        self.reader.start();


    def stop(self):
        """ """
        self.alive=False;


    def rxq_flush(self):
        """ """
        while not rxq.empty():
            rxq.get()


    def send_msg(self, msg):
        """ Send the passed Msg object """
        self.serial.write(msg.msg_str())
        if self.debug:
            sys.stdout.write("TX ");
            msg.print_msg()


    def send_recv(self, msg):
        """ Send passed message then wait to receive a message in response, 
        return the received Msg object or None if no message received."""
        self.send_msg(msg)
        rmsg = self.get_msg()
        if rmsg == None:
            pass
        return rmsg;
            

    def handle_msg(self, msg):
        """ Callback for when messsage has been received, add it to the queue"""
        self.rxq.put(msg)
        if self.debug:
            sys.stderr.write('RX: ')
            msg.print_msg()


    def get_msg(self):
        """ """
        try:
            msg=self.rxq.get(True, self.timeoutSec);
            if self.debug:
                sys.stdout.write("RX ");
                msg.print_msg()
            return msg
        except Queue.Empty,e:
            return None;


    def read_char(self):
        "Callback for when a new received char is required. Reads from the serial port"
        return self.serial.read(1);


    def handle_log_str(self, logstr):
        """ Callback for when log string has been received from MCU, prints to stderr """
        sys.stderr.write('MCU LOG'+logstr + '\n');

        
    def handle_non_msg_char(self, c):
        """ Call by reader_thred when a character is received that is not part of a message, nor part of a LOG string"""
        #sys.stdout.write(c)
        pass


    def _create_msg(self):
        """ Factory method to create message object """
        return Msg();


    def reader_thread(self):
        """ """

        # states
        SIDLE  = 0
        SLOG   = 1
        SDATA  = 2
        SLEN   = 3
        
        logi = 0;
        state = SIDLE;
        logstr = '';
        msg = self._create_msg();

        try:
            while self.alive:
                c = self.read_char();
                if(c):
                    # char was received
                    if state == SIDLE:
                        if c == Msg.MSG_SOM:
                            # got start byte
                            logi = 0
                            state = SLEN
                            msg = self._create_msg();
                        else:
                            if c == self.LOGS[logi]:
                                # got a LOGS char
                                logi += 1
                                if logi == len(self.LOGS):
                                    # Yup, this is a LOG string
                                    #logstr=self.LOGS;
                                    logstr=''
                                    state = SLOG
                                    logi=0;
                            else:
                                # nope, false alarm, char received was not start of message, not start of log string
                                logi=0;
                                self.handle_non_msg_char(c)
                    elif state == SLOG:
                        # we're receiving a log msg
                        if c == '\n':
                            # this is end of log string
                            self.handle_log_str(logstr)
                            state = SIDLE
                            logstr = '';
                        else:
                            logstr = logstr + c;
                            if len(logstr) > self.LOGS_MAX:
                                logging.warn("log string is too long. Truncated: "+logstr+"\n")
                                self.log_str_received(logstr)
                                state = SIDLE
                                logstr = '';
                    elif state == SLEN:
                        # recived char is message length
                        msg.len = ord(c)
                        state = SDATA
                    elif state == SDATA:
                        if msg.is_complete():
                            # have received all the data, looking for EOM
                            if c == Msg.MSG_EOM:
                                # yep, got EOM, message is complete
                                self.handle_msg(msg)
                                state = SIDLE;
                            else:
                                # did not get EOM, but should have
                                logging.error("msg EOM not received: "+str(msg.data))
                                if self.debug:
                                    logging.warning("msg EOM not received:\n");
                                    msg.print_msg();
                                state = SIDLE;
                        else:
                            # we're receiving msg data, add rx char to message
                            msg.rx_char(c)

                else:
                    #char was not received, ie timeout
                    state = SIDLE
                    pass

        except Exception, e:
            sys.stderr.write("Caught exception in reader thread: ");
            traceback.print_exc(e)
            raise e
            pass;
