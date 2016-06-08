# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015 - 2016. http://telecnatron.com/
# $Id: $
# -----------------------------------------------------------------------------
import sys
from CLI import CLI

class CmdCli(CLI):
    """ Msg test command interpreter"""
    
    def __init__(self, cmd_handler, interactive=True):
        """ """
        self.cmd_handler = cmd_handler;
        CLI.__init__(self, interactive, name='Msg')


    def cmd_done(self):
        """ """
        CLI.cmd_done(self, self.cmd_handler.cmd_status, self.cmd_handler.cmd_msg)
        

    def do_reset(self, arg):
        """Reset the MCU """
        self.cmd_test.resetMCU()


    def do_ping(self, arg):
        """ping <count=1>\nPing the MCU 'count' number of times"""
        count = 1;        
        try:
            if arg:
                count = int(arg)
        except ValueError:
            self.write_error("ping: invalid argument\n")
            self.cmd_done(exit_status=255, error_msg = 'invalid argument')
            return
        self.cmd_handler.cmd_ping(count)
        self.cmd_done()


    def do_led(self, arg):
        """ """
        arg = arg.upper()
        self.cmd_done();


