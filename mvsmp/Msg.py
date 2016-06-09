# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import logging
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
        # expected length of the message being recived
        self._rxlen=len;
        # count of the number of data bytes received so far
        self._rxcount=0;


    def rx_char(self, c):
        """ add passed char to the msg that is being received"""
        print "msgc: "+str(c)+","
        self.data.extend(c)
        self._rxcount += 1


    def rx_is_complete(self):
        """ Returns true if message has been completely received. ie len == count """
        if self._rxlen == self._rxcount:
            return True
        else:
            return False


    def tx_char(self, c):
        """ add passed char to msg that is to be transmitted """
        self.data.extend(c)
        

    def get_len(self):
        """ """
        return len(self.data);

    def _msg_str_SOM(self):
        """pack SOM and length """
        return pack('<cB', self.MSG_SOM, self.get_len());

    def _msg_str_EOM(self):
        """pack EOM """
        return  pack('<c', self.MSG_EOM);


    def _pack_msg_data(self):
        """Called by self.msg_str(): return string of packed data chars"""
        msg= '';
        for ch in self.data:
            msg+=pack('<c',ch);
        return msg;


    def msg_str(self):
        """ Return binary string suitable for transmission"""
        # 
        msg =  self._msg_str_SOM()
        msg += self._pack_msg_data()
        msg += self._msg_str_EOM();
        return msg


    def str(self):
        """ """
        str= "msg: len: %2i, data: " % self._len
        str = str+ ''.join("-"+format(b, '02x') for b in self.data)
        str = str + " str: "+self.data
        return str


    def print_msg(self):
        """ """
        sys.stderr.write(self.str()+"\n")

