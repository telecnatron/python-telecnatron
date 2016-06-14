# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import logging
import threading

from CmdMsgHandler import CmdMsgHandler;
from CmdMsg import CmdMsg;

# -------------------------------------------        
class AsyncCmdHandler():
    """ Base class that handler async messages coming from CmdMsgHandler object """

    def __init__(self, cmd_msg_handler):
        """ """
        self.cmd_msg_handler = cmd_msg_handler;
        self.asyncReader = threading.Thread(target  = self.reader_thread)
        self.alive = True
        self.asyncReader.start()


    def reader_thread(self):
        """ Thread polls cmd_msg_handler for async command messges"""
        while self.alive:
            msg=self.cmd_msg_handler.get_async_msg(2)        
            if msg != None:
                self.handle_msg(msg)

    
    def handle_msg(self, cmdmsg):
        """ """
        if(cmdmsg.get_cmd() == CmdMsgHandler.CMD_BOOTLOADER_STARTED):
            logging.info("ASYNC: bootloader start detected");
        elif (cmdmsg.get_cmd() == CmdMsgHandler.CMD_APP_STARTED):
            logging.info("ASYNC: application start detected");
        else:
            logging.info("ASYNC: "+cmdmsg.str());


