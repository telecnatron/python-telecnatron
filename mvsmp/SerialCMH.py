# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2016. http://telecnatron.com/
# -----------------------------------------------------------------------------
import sys
import serial
import logging
from CmdMsgHandler import CmdMsgHandler

# -------------------------------------------        
class SerialCMH(CmdMsgHandler):
    """Extends Command Message Handler by reading and writing messages to and from the serial port"""

    def __init__(self, port, baud, timeout_sec=2):
        """ """
        try:
            # create serial port object, open port
            self.serial = serial.Serial(port, baud, timeout=timeout_sec);
        except Exception, e:
            logging.error("Could not open serial port %s: %s\n" % (port, e))
            raise e;
        # call parent class's init.
        CmdMsgHandler.__init__(self, timeout_sec)


    def read_char(self):
        """Reads and returns a character read from the transport stream (self.serial in this case),
        or returns None if no character is available.
        """
        return self.serial.read(1);


    def write(self, datas):
        """ """
        self.serial.write(datas)
        


