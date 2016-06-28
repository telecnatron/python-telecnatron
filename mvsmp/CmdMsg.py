# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import logging
from struct import * 
from Msg import Msg;



class CmdMsg(Msg):
    """A message type derived from Msg class in which the first byte of the data is a command-number"""

    def __init__(self, cmd = 0):
        """ """
        Msg.__init__(self)
        self.cmd=cmd;


    def rx_char(self, c):
        """ Add passed char to the msg data that is being received."""
        # first received char is the command number
        if self._rxcount == 0:
            self.cmd = ord(c);
        else:
            self.data.extend(c)
        self._rxcount += 1


    def get_len(self):
        """Return the lenght of the message data."""
        # add one byte for the command
        return len(self.data)+1;


    def _pack_msg_data(self):
        # pack command char
        msg = pack('<B',self.cmd)[0];
        self.sum+=self.cmd;
        # pack data chars
        for ch in self.data:
            self.sum += ch
            msg += pack('<B',ch);
        return msg;


    def __str__(self):
        """Return a string being human readible representation of the object's data."""
        s= "CmdMsg: cmd: %02x, len: %2i, data_len: %2i, data: " % (self.get_cmd(), self.get_len(), len(self.data))
        s = s + ''.join("-"+format(b, '02x') for b in self.data[0::])
        #s = s + " str: " + str(self.data[1::])
        return s


    def get_cmd(self):
        """Return byte (char) being the message's command number """
        return self.cmd

       
