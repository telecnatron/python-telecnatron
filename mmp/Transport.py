# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2017. http://telecnatron.com/
# -----------------------------------------------------------------------------
#/**
# * @file   Transport.py
# * @author steves
# * @date   2017/02/18 23:00:08
# * 
# * @brief  
# * 
# */
import serial, logging

# -----------------------------------------------------------
class Transport:
    """ Abstract network-transport class, provides read/write/timeout methods. eg Serial port. """

    def __init__(self):
        """ """
        pass;

    def readByte(self):
        """ """
        return None;


    def write(self, databytes):
        """ """
        pass;


    def setTimeout(self, timeoutSec):
        """ """
        self.serial.timeout=timeoutSec
        pass


# -----------------------------------------------------------
class SerialTransport:
    """ Network-transport class for the serial port """
    def __init__(self, port, baud=19200, timeoutSec=0.004):
        """ """
        try:
            # create serial port object, open port
            self.serial = serial.Serial(port, baud, timeout=timeoutSec);
        except Exception, e:
            logging.error("Could not open serial port {}: {}\n".format(port, e))
            raise e;


    def readByte(self):
        """ """
        return self.serial.read(1);


    def write(self, databytes):
        """ """
        return self.serial.write(databytes);


    def setTimeout(self, timeoutSec):
        """ """
        pass






