# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import logging
from struct import * 
from Msg import Msg;


class CmdMsg(Msg):
    """ """

    # max MSG_ID of async messages
    MSG_ID_ASYNC_MAX = 7
    MSG_ID_INVALID = -1;

    def __init__(self, cmd = 0):
        """ """
        Msg.__init__(self,0)
        # first byte of self.data is the command
        self.cmd=cmd;


    def rx_char(self, c):
        """ add passed char to the msg that is being received"""
        # first received char is the command number
        if self._rxcount == 0:
            self.cmd = ord(c);
        else:
            self.data.extend(c)
        self._rxcount += 1


    def get_len(self):
        """ """
        # add one byte for the command
        return len(self.data)+1;


    def _pack_msg_data(self):
        """Called by self.msg_str(): return string of packed data chars"""
        # pack command char
        msg = pack('<B',self.cmd)[0];
        # pack data chars
        for ch in self.data:
            msg += pack('<c',ch);
        return msg;


    def str(self):
        """ """
        str= "CmdMsg: cmd: %02x, len: %2i, data_len: %2i, data: " % (self.get_cmd(), self.get_len(), len(self.data))
        str = str+ ''.join("-"+format(b, '02x') for b in self.data[1::])
        str = str + " str: "+self.data[1::]
        return str


    def get_cmd(self):
        """ """
        return self.cmd

        
    def is_async(self):
        """ """
        cmd = self.get_cmd()
        if(cmd >= 0 and cmd <= self.MSG_ID_ASYNC_MAX):
            return True;
        else:
            return False;


    def is_cmd(self):
        """Return true if cmd is a non-async command"""
        return not self.is_async()
