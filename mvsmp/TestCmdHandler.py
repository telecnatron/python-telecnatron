# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import os
import Queue
#from struct import * 
from CmdMsgHandler import CmdMsgHandler;

# -------------------------------------------        
class TestCmdHandler(CmdMsgHandler):
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

    def cmd_ping(self, count):
        """ """
        print "ping"
