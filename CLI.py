# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015 - 2016. http://telecnatron.com/
# -----------------------------------------------------------------------------
import cmd
import sys
import logging

class CLI(cmd.Cmd):
    """ Command line interface class. Wrapper for the cmd class. 
    * Implements 'exit' cmd which exits cmd interpreter loop
    * Call cmdloop() method to run the interpreter
    """
    
    def __init__(self, interactive=True, name=''):
        """ """
        cmd.Cmd.__init__(self)
        self.prompt = ''
        self.ruler=''
        # command line tokenized into individual arguments
        self.args = []
        # Flag to indicate whether shell is an interactive shell
        self.interactive = interactive
        if interactive:
            self.prompt = '>'
            self.intro= 'command interpreter. See http://telecnatron.com/articles/mvsmp'
            if name:
                self.intro= name + ' ' + self.intro
        # exit status of last command: 0 - 255, 0 indicating success, non-zero flagging an error
        self.exit_status = 0;


    def _log(self, msg):
        """ """
        logging.info(msg);

        
    def postcmd(self, stop, line):
        """ """
        if stop:
            return True
        else:
            return False;

    def precmd(self, line):
        """ """
        self.args=line.split()
        return line

    def argv(self, arg_num):
        """ """
        return self.args[arg_num]

    def argc(self):
        """ """
        return len(self.args)

    def emptyline(self):
        """ """
        pass

    def default(self, line):
        """ """
        msg="ERROR({}): unrecognised command: {}".format(255,line.split()[0])
        self._log(msg)
        if self.interactive:
            print msg


    def cmd_done(self, exit_status = 0, error_msg = ''):
        """ """
        self.exit_status = exit_status;
        if( exit_status != 0):
            # display error message
            msg="ERROR({}): {}".format(exit_status,error_msg)
            self._log(msg)
            if self.interactive:
                print msg


    def do_EOF(self, line):
        """Exit the command interpreter on CTRL-D"""
        return True


    def do_exit(self, line):
        """Exit the command interpreter"""
        self.do_EOF(line)
        return True;



