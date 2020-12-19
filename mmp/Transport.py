# ------------------------------------------------------------------------------
# Copyright 2020 Stephen Stebbing. telecnatron.com
#
#    Licensed under the Telecnatron License, Version 1.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://telecnatron.com/software/licenses/
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ------------------------------------------------------------------------------
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






