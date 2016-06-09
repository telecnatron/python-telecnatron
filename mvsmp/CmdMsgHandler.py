# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import os
import Queue
import logging
#from struct import * 
from MsgHandler import MsgHandler;
from CmdMsg import CmdMsg;

# -------------------------------------------        
class CmdMsgHandler(MsgHandler):
    """ """
    # max number of items that may be in command response queue
    CMDR_QUEUE_MAX  = 8
    # max number of items that may be in async queue
    ASYNC_QUEUE_MAX = 8
   
    def __init__(self, port, baud, timeoutSec):
        """ """
        # call parent class's init.
        MsgHandler.__init__(self, port, baud, timeoutSec);
        # queue for command response messages
        self.cmdrq = Queue.Queue(maxsize=self.CMDR_QUEUE_MAX);
        # queue for command response messages
        self.asyncq = Queue.Queue(maxsize=self.ASYNC_QUEUE_MAX);
        self.cmd_status=0;
        self.cmd_msg = ''


    def _create_msg(self):
        """ Factory method to create message object """
        return CmdMsg();


    def get_async_msg(self):
        """ """
        try:
            msg=self.asyncq.get(True, self.timeoutSec);
            return msg
        except Queue.Empty,e:
            return None;


    def get_cmd_msg(self):
        """ """
        try:
            msg=self.cmdrq.get(True, self.timeoutSec);
            return msg
        except Queue.Empty,e:
            return None;

    def get_msg(self):
        """ """
        return self.get_cmd_msg()


    def asyncq_flush(self):
        """ """
        while not self.asyncq.empty():
            self.asyncq.get()


    def cmdq_flush(self):
        """ """
        while not self.cmdrq.empty():
            self.cmdrq.get()


    def reset_mcu(self):
        """ Reset MCU by sending it reset msg """
        logging.debug("reset");
        m = CmdMsg(0);
        self.send_msg(m)


    def handle_msg(self, msg):
        """ """
        # put msg on appropiate queue depending on whether it was received async or not
        if msg.is_async():
            self.asyncq.put(msg);
        else:
            self.cmdrq.put(msg);
        if self.debug:
            if msg.is_async():
                logging.debug('RX ASYNC: '+msg.str())
            else:
                logging.debug('RX CMD: '+msg.str())

            




