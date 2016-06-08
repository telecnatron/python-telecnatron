# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
from struct import * 


class Msg:
    """ """

    # char indicating start of message
    MSG_SOM='\2'
    # char indicating end of message
    MSG_EOM='\3'

    def __init__(self, len=0):
        """ """
        self.data=bytearray();
        # (Expected) length of the message.
        self.len=len;
        # count of the number of data bytes received so far
        self._count=0;

    def rx_char(self, c):
        """ add passed char to the message """
        self.data.extend(c)
        self._count += 1
        
    def is_complete(self):
        """ Returns true if message has been completely received. ie len == count """
        if self.len == self._count:
            return True
        else:
            return False

    def msg_str(self):
        """ """
        # make passed string into list (array) of chars 
        mlist=list(msgS);
        # pack SOM and length
        msg=pack('<cB', self.MSG_SOM, len(mlist));
        # pack data bytes
        for ch in mlist:
            msg+=pack('<c',ch);
        # pack EOM
        return msg + pack('<c', self.MSG_EOM);


    def str(self):
        """ """
        str= "msg: len: %2i, data: " % self.len
        str = str+ ''.join("-"+format(b, '02x') for b in self.data)
        str = str + " str: "+self.data
        return str


    def print_msg(self):
        """ """
        sys.stderr.write(self.str()+"\n")

