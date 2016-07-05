# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import logging
from struct import * 


class Msg:
    """Base class for mvsmp message.

    A message comprises of unsigned 8-bit byte (char) elements, these being:
       * start of message byte as defined by Msg.MSG_SOM.
       * length byte. It's value being the number of following data bytes. Hence 255 being the maximum data length.
       * data bytes. Their number being equal to the value of the length byte
       * checksum byte: The checksum is equal to the number that is added to the (8-bit) sum of the length and data bytes
         to make the resulting value be equal to zero.

    That self.data is a bytearray object, it is used to hold the bytes comprising the msg data
    """

    #char indicating start of message
    MSG_SOM='\2'

    def __init__(self):
        """Initiase an object of this class"""
        
        self.data=bytearray()
        # expected length of the message being recived
        self._rxlen=len;
        # count of the number of data bytes received so far
        self._rxcount=0;
        # count of rx bytes used for checksum calculation
        self.sum = 0;


    def rx_char(self, c):
        """ Add passed char to the msg data that is being received."""
        self.data.extend(c)
        # accumulate checksum sum
        self.sum += ord(c) % 256;
        self._rxcount += 1


    def rx_is_complete(self):
        """ Returns true if message has been completely received. ie _rxlen == _rxcount."""
        if self._rxlen == self._rxcount:
            return True
        else:
            return False


    def tx_char(self, c):
        """Append passed char to self.data"""
        self.data.extend(c)
        

    def get_len(self):
        """Return the lenght of the message data."""
        return len(self.data);


    def _msg_str_SOM(self):
        """Return string comprising start of message character and data length."""
        self.sum=self.get_len();
        return pack('<cB', self.MSG_SOM, self.get_len());


    def _msg_str_CS(self):
        """Calculate checksum based on self.sum and return it as string comprising one unsigned byte"""
        cs= (256 - self.sum) % 256
        return  pack('<B', cs);


    def _pack_msg_data(self):
        """Return a string of packed unsigned bytes being the bytes comprising the self.data bytearray."""
        msg= '';
        for ch in self.data:
            self.sum += ord(ch)
            msg += pack('<B',ch);
        return msg;


    def msg_str(self):
        """Return binary string comprising the message, suitable for transmission"""
        # 
        msg =  self._msg_str_SOM()
        msg += self._pack_msg_data()
        msg += self._msg_str_CS();
        return msg


    def __str__(self):
        """Return a string being human readible representation of the object's data."""
        s= "msg: len: %2i, data: " % self._rxlen
        s = s + ''.join("-"+format(b, '02x') for b in self.data)
        s = s + " str: "+str(self.data)
        return s



