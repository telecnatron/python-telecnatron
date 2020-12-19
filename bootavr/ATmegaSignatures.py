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
class ATmegaSignatures:
    """Get infomation on a MCU's type and its memory info based on it's signature.
    """

    def MCU(self, sig):
        """Return a string being the name of the MCU with given signature string.
        
        Args:
            sig (str) the signature as return by the MCU

        Returns:
           str: MCU name or None if the signature is unrecognised
        
        """
        return self.signatures.get(sig);

    def getMCUInfo(self,sig):
        """Get information on device with the passed signature

        The information returned is a dictionary with the following fields:
            {'name':'ATMEGA48',  'flashSizeBytes':4096,  'pageSizeBytes':64, 'eepromSizeBytes':  256}

        Note that currently only the first 4 characters of the signature string
        are used. See this class's mcu_info dictionary for what signatures are recognised.

        Args:
            sig (str) the signature as returned by the MCU

        Returns:
            Dictionary containg the info, or None if the signature is unrecognised.
            
        """
        return self.mcu_info.get(sig[:4]);

    def __init__(self):
        """Initialise the class's 'signatures' and 'mcu_info' dictionaries.
        """
        # dictionary of signatures
        self.signatures={
            '1E9703':'ATMEGA1280',
            '1E9704':'ATMEGA1281',
            '1E9705':'ATMEGA1284P',
            '1E9706':'ATMEGA1284',
            '1E9702':'ATMEGA128A',
            '1EA701':'ATMEGA128RFA1',
            '1E9702':'ATMEGA128',
            '1E9404':'ATMEGA162',
            '1E940F':'ATMEGA164A',
            '1E940A':'ATMEGA164PA',
            '1E940A':'ATMEGA164P',
            '1E9410':'ATMEGA165A',
            '1E9407':'ATMEGA165PA',
            '1E9407':'ATMEGA165P',
            '1E9406':'ATMEGA168A',
            '1E940B':'ATMEGA168PA',
            '1E940B':'ATMEGA168P',
            '1E9406':'ATMEGA168',
            '1E9411':'ATMEGA169A',
            '1E9405':'ATMEGA169PA',
            '1E9405':'ATMEGA169P',
            '1E9403':'ATMEGA16A',
            '1E940D':'ATMEGA16HVB',
            '1E9484':'ATMEGA16M1',
            '1E9489':'ATMEGA16U2',
            '1E9488':'ATMEGA16U4',
            '1E9403':'ATMEGA16',
            '1E9801':'ATMEGA2560',
            '1E9802':'ATMEGA2561',
            '1E9515':'ATMEGA324A',
            '1E9511':'ATMEGA324PA',
            '1E9508':'ATMEGA324P',
            '1E9506':'ATMEGA3250A',
            '1E950E':'ATMEGA3250PA',
            '1E950E':'ATMEGA3250P',
            '1E9506':'ATMEGA3250',
            '1E9505':'ATMEGA325A',
            '1E950D':'ATMEGA325PA',
            '1E950D':'ATMEGA325P',
            '1E9505':'ATMEGA325',
            '1E950F':'ATMEGA328P',
            '1E9514':'ATMEGA328',
            '1E9504':'ATMEGA3290A',
            '1E950C':'ATMEGA3290PA',
            '1E950C':'ATMEGA3290P',
            '1E9504':'ATMEGA3290',
            '1E9503':'ATMEGA329A',
            '1E950B':'ATMEGA329PA',
            '1E950B':'ATMEGA329P',
            '1E9503':'ATMEGA329',
            '1E9502':'ATMEGA32A',
            '1E9586':'ATMEGA32C1',
            '1E9510':'ATMEGA32HVB',
            '1E9584':'ATMEGA32M1',
            '1E958A':'ATMEGA32U2',
            '1E9587':'ATMEGA32U4',
            '1E9502':'ATMEGA32',
            '1E9205':'ATMEGA48A',
            '1E920A':'ATMEGA48PA',
            '1E920A':'ATMEGA48P',
            '1E9205':'ATMEGA48',
            '1E9608':'ATMEGA640',
            '1E9609':'ATMEGA644A',
            '1E960A':'ATMEGA644PA',
            '1E960A':'ATMEGA644P',
            '1E9609':'ATMEGA644',
            '1E9606':'ATMEGA6450A',
            '1E960E':'ATMEGA6450P',
            '1E9606':'ATMEGA6450',
            '1E9605':'ATMEGA645A',
            '1E960D':'ATMEGA645P',
            '1E9605':'ATMEGA645',
            '1E9604':'ATMEGA6490A',
            '1E960C':'ATMEGA6490P',
            '1E9604':'ATMEGA6490',
            '1E9603':'ATMEGA649A',
            '1E960B':'ATMEGA649P',
            '1E9603':'ATMEGA649',
            '1E9602':'ATMEGA64A',
            '1E9686':'ATMEGA64C1',
            '1E9684':'ATMEGA64M1',
            '1E9602':'ATMEGA64',
            '1E9306':'ATMEGA8515',
            '1E9308':'ATMEGA8535',
            '1E930A':'ATMEGA88A',
            '1E930F':'ATMEGA88PA',
            '1E930F':'ATMEGA88P',
            '1E930A':'ATMEGA88',
            '1E9307':'ATMEGA8A',
            '1E9389':'ATMEGA8U2',
            '1E9307':'ATMEGA8'
        };


        self.mcu_info={
            '1E92':{'name':'ATMEGA48',  'flashSizeBytes':4096,  'pageSizeBytes':64, 'eepromSizeBytes':  256},
            '1E93':{'name':'ATMEGA88',  'flashSizeBytes':8192,  'pageSizeBytes':64, 'eepromSizeBytes':  512},
            '1E94':{'name':'ATMEGA168', 'flashSizeBytes':16384, 'pageSizeBytes':128, 'eepromSizeBytes': 512},
            '1E95':{'name':'ATMEGA328', 'flashSizeBytes':32768, 'pageSizeBytes':128, 'eepromSizeBytes': 1024},
        };




