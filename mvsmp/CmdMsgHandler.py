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

class CmdMsgException(Exception):
    """Exception class that is used by CmdMsgHandler to raise exceptions """
    pass

# -------------------------------------------        
class CmdMsgHandler(MsgHandler):
    """ """

    # predefine cmd numbers.
    CMD_REBOOT=              255
    CMD_BOOTLOADER_STARTED=  254
    CMD_APP_STARTED=         253

    # Command messages with cmd number equal to greater than this are considered to be 
    # async commands.
    _CMD_ASYNC_MIN = 240
    # max number of items that may be in command response queue
    _CMDR_QUEUE_MAX  = 8
    # max number of items that may be in async queue
    _ASYNC_QUEUE_MAX = 8
   
    def __init__(self, port, baud, timeoutSec):
        """ """
        # call parent class's init.
        MsgHandler.__init__(self, port, baud, timeoutSec);
        # queue for command response messages
        self.cmdrq = Queue.Queue(maxsize=self._CMDR_QUEUE_MAX);
        # queue for command response messages
        self.asyncq = Queue.Queue(maxsize=self._ASYNC_QUEUE_MAX);
        # exit status and msg as return by a command
        self.cmd_status=0;
        self.cmd_msg = ''


    def send_recv(self, msg):
        """ Flushes the cmd queue, sends passed msg then returns the msg that was received in response,
        or throws CmdMsgHandlerException if no response message is received"""
        self.cmdq_flush()
        self.send_msg(msg);
        rmsg = self.get_cmd_msg();
        if rmsg == None:
            raise CmdMsgException("did not receive response msg for sent msg with cmd: "+str(hex(msg.get_cmd()))+' ['+str(msg.get_cmd())+']');
        return rmsg;


    def cmd_result(self, status=0, msg=""):
        """ """
        self.cmd_status = status;
        self.cmd_msg = msg;


    def msg_is_async(self, msg):
        """Return true if messages's command number is and async command number, false otherwise """
        if( msg.get_cmd() >= self._CMD_ASYNC_MIN):
            return True;
        else:
            return False;


    def _create_msg(self):
        """ Factory method to create message object """
        return CmdMsg();


    def get_async_msg(self, timeoutSec=2):
        """ """
        try:
            msg=self.asyncq.get(True, timeoutSec);
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
        if self.msg_is_async(msg):
            self.asyncq.put(msg);
        else:
            self.cmdrq.put(msg);
        if self.debug:
            if msg.is_async():
                logging.debug('<--RX ASYNC: '+msg.str())
            else:
                logging.debug('<--RX CMD: '+msg.str())

            




