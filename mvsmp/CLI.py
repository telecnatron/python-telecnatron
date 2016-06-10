# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015 - 2016. http://telecnatron.com/
# $Id: $
# -----------------------------------------------------------------------------
import cmd
import sys
import logging

class CLI(cmd.Cmd):
    """ Command line interface class. """
    
    def __init__(self, interactive=True, name=''):
        """ """
        cmd.Cmd.__init__(self)
        self.prompt = ''
        self.ruler=''
        # Flag to indicate whether shell is an interactive shell
        self.interactive = interactive
        if interactive:
            self.prompt = '>'
            self.intro= 'command interpreter. See http://telecnatron.com'
            if name:
                self.intro= name + ' ' + self.intro
        # exit status of last command: 0 - 255, 0 indicating success, non-zero flagging an error
        self.cmd_exit_status = 0;
        self.cmd_exit_msg = ''


   
    def default(self,line):
        """ """
        self.write_error("Unrecognised command: "+line);

        
    def postcmd(self, stop, line):
        """ """
        if stop:
            return True
        else:
            return False;

    def emptyline(self):
        """ """
        pass


    def write(self, msg):
        """ """
        sys.stdout.write(msg)


    def write_error(self, msg, code = 255):
        """ """
        m="Error: {:2d}: {!s}".format(code, msg)
        logging.debug(m);
        self.write(m+'\n')


    def cmd_done(self, exit_status = 0, exit_msg = ''):
        """ """
        self.cmd_exit_status = exit_status;
        self.cmd_exit_msg = exit_msg;
        if( exit_status != 0):
            # display error message
            self.write_error(exit_msg, exit_status)


    def do_EOF(self, line):
        """Exit the command interpreter on CTRL-D"""
        return True


    def do_exit(self, line):
        """Exit the command interpreter"""
        self.do_EOF(line)
        return True;



