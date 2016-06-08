# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
from struct import * 
from Msg import Msg;


class CmdMsg(Msg):
    """ """

    # max MSG_ID of async messages
    MSG_ID_ASYNC_MAX = 7
    MSG_ID_INVALID = -1;

    def __init__(self, len=0):
        """ """
        Msg.__init__(self,len)


    def str(self):
        """ """
        str= "CmdMsg: cmd: %02x len: %2i, data: " % (self.get_cmd(), self.len-1)
        str = str+ ''.join("-"+format(b, '02x') for b in self.data[1::])
        str = str + " str: "+self.data[1::]
        return str


    def get_cmd(self):
        """ """
        cmd = -1;
        if self.len:
            cmd = self.data[0]
        return cmd

        
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
