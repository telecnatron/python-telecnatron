# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import logging
from struct import * 
from Msg import Msg;


class CmdMsg(Msg):
    """ """

    def __init__(self, cmd = 0):
        """ """
        Msg.__init__(self,0)
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
        self.sum+=self.cmd;
        # pack data chars
        for ch in self.data:
            self.sum += ord(ch)
            msg += pack('<B',ch);
        return msg;


    def str(self):
        """ """
        str= "CmdMsg: cmd: %02x, len: %2i, data_len: %2i, data: " % (self.get_cmd(), self.get_len(), len(self.data))
        str = str+ ''.join("-"+format(b, '02x') for b in self.data[0::])
        str = str + " str: "+self.data[1::]
        return str


    def get_cmd(self):
        """ """
        return self.cmd

       
    def is_cmd(self):
        """Return true if cmd is a non-async command"""
        return not self.is_async()
