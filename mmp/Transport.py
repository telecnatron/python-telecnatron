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
    """ Abstract network-transport class for reading/writing bytes to a serial stream,
    provides read/write/timeout methods. eg Serial port. 
    """

    def __init__(self):
        """Initialise the object and do nothing else"""
        pass;

    def readByte(self):
        """Abstract method that reads a byte (char, octet or whatever) from the transport stream and returns it.
        :returns: The char read from the transport stream, or None if none was available
        :rtype: char or None
        """
        return None;


    def write(self, databytes):
        """Abstract method: write passed databytes (string, bytearray) to the transport stream"""
        pass;


    def setTimeout(self, timeoutSec):
        """Abstract method: set the transport's stream's read timeout. If read() does not receive a byte
        withing this number of seconds (may be < 1) then an error has occured."""
        pass


# -----------------------------------------------------------
class SerialTransport(Transport):
    """ Network-transport class for the serial port """

    def __init__(self, port, baud=19200, timeoutSec=0.004):
        """Initialise serial port transport stream
        :param port: The port. eg /dev/ttyUSB0
        :param baud: The baud rate
        :param timeoutSec: Timeout value for readByte()
        """
        try:
            # create serial port object, open port
            self.serial = serial.Serial(port, baud, timeout=timeoutSec);
        except Exception, e:
            logging.error("Could not open serial port {}: {}\n".format(port, e))
            raise e;


    def readByte(self):
        """Read a byte from the serial port and returns it.
        :returns: The byte read from the serial port, or None if no byte was available.
        """
        return self.serial.read(1);


    def write(self, databytes):
        """Write passed data to serial port
        :param databytes: string or bytearray etc of data to be written
        """
        return self.serial.write(databytes);


    def setTimeout(self, timeoutSec):
        """ 
        Set timeout for readByte();
        :param timeoutSec: Number of seconds for timeout. Float and <1 is okay.

        """
        self.serial.timeout=timeoutSec







