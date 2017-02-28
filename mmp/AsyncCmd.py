# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2017. http://telecnatron.com/
# -----------------------------------------------------------------------------
#/**
# * @file   AsyncCmd.py
# * @author steves
# * @date   2017/02/22 00:56:10
# * 
# */
import logging;
import Queue;
from MMP import *;


class CmdResponseMsg(MMPMsg):
    """Class extends MMPMsg class to support command-response messages"""
    def __init__(self):
        """Initialise the class. """
        MMPMsg.__init__(self)
        # the command-number of the command that was executed.
        self.cmd = 0;
        # the status returned by the command that was executed.
        self.status = 0;

    def __str__(self):
        """Return a string representation of the object"""
        return "cmd: {}, status: {}: {}".format(self.cmd, self.status, MMPMsg.__str__(self));
        

class AsyncCmd(MMP):
    """Implementation of command-response messages and async messages.

    Command-response messaging involves the  PC sending a command message, with the MCU executing
    the command contained therein, and replying with a command-response message.

    Async messages are those sent by the MCU asynchronously, ie not in response to a command message, and might
    typically, for example, be used to signal that a button has been pushed.

    The 'flags' member of the MMPMsg class is used to distinguish whether messages being received by the PC are 
    command(-response) messages or async messages.

    On receipt, async messages are added to a Queue called the async queue. They may be accessed via the
    asyncMsgAvailable() and asyncMsgGet() methods.

    The sendReceiveCmd() method is used to send a command-message to the MCU and return its response message.
    """

    # message FLAGS that we recognise
    FLAGS_ASYNC = 0x02
    FLAGS_CMD   = 0x01

    def __init__(self, transport=None):
        """ 
        :param transport: (Reference to) object of class mmp.Transport that is used to send and receive bytes on the communications channel.
        """
        MMP.__init__(self, transport);
        # init queue for async messages
        self.asyncq = Queue.Queue(maxsize=16);
        # init queue for cmd messages
        self.cmdq = Queue.Queue(maxsize=1);
        # keep track of number of messages received:
        # number of async messages that have been received
        self.num_async = 0;
        # number of command messages that have been sent.
        self.num_cmd = 0;
        # number of command-response messages that have been received.
        self.num_responses = 0;
        # Tallies of various errors:
        self.errors_unrecognised_msg = 0
        self.errors_invalid_cmd_response = 0
        self.errors_response_timeout = 0


    def handleMsg(self, msg):
        """Handle messages received from MCU by placing them in the async queue or the cmd queue, as
        appropiate."""
        # add message to appropiate queue
        logging.debug("got msg: {}".format(msg));
        if msg.flags & self.FLAGS_ASYNC:
            logging.debug("added msg to async queue");
            self.num_async += 1
            self.asyncq.put(msg)
        elif msg.flags & self.FLAGS_CMD:
            logging.debug("added msg to cmd queue");
            self.num_cmd += 1
            self.cmdq.put(msg);
        else:
            logging.warn("Unhandled msg flags: {}".format(msg));
            self.errors_unrecognised_msg += 1

    def asyncMsgAvailable(self):
        """Return true if there is one or more async messages available (in the async queue)"""
        return not self.asyncq.empty()

    def asyncMsgGet(self):
        """Get async message from the head of the async queue and return it, or None if none is available.
        :returns: AsyncMsg object or None
        """
        if not self.asyncq.empty():
            return self.asyncq.get_nowait()
        else:
            return None


    def sendReceiveCmd(self, cmd, msgData, timeoutSec = 0.5):
        """ Send a message with passed command-number to MCU, wait for and return response message.
        Return None if there is no response or if timeout or other error is detected.

        :param cmd: The command number (must be 8-bit unsigned char)
        :param msgData: The message data that is to be sent in the command-message. String or bytearray.
        :param timeoutSec: (float) The number of seconds to wait for the resonse message. May be fractional.
        :returns: CmdResponseMessage object (reference) or None.
        """
        # flush rx queue
        while not self.cmdq.empty():
            self.cmdq.get_nowait();
        # prepend the msgData with the cmd byte, and empty byte being for response STATUS field.
        msgData = pack("<BB", cmd, 0)+msgData
        # send msg
        self.sendMsg(msgData, flags=self.FLAGS_CMD);
        # wait for response
        try:
            # get response message
            rmsg= self.cmdq.get(True, timeoutSec)
            # make a new cmd-response objetc
            crmsg = CmdResponseMsg();
            crmsg.flags = rmsg.flags;
            # response data length must be at least two, data[0] being the cmd number, data[1] being the status byte
            if rmsg.len  < 2:
                logging.warn("invalid response message for cmd: {}: msg: {}".format(cmd, rmsg))
                self.errors_invalid_cmd_response += 1
                return None
            # check cmd byte from response message
            crmsg.cmd = rmsg.data[0];
            if not crmsg.cmd == cmd:
                # invalid response: cmd field of received message did not match that of sent message
                logging.warn("invalid response to cmd: {}: {}".format(cmd, rmsg));
                self.errors_invalid_cmd_response += 1
                return None
            # extract status code from the data
            crmsg.status = rmsg.data[1];
            # valid response, remove the cmd and status bytes from data
            crmsg.data= rmsg.data[2:]
            crmsg.len = len(crmsg.data)
            self.num_responses += 1
            return crmsg;
        except Queue.Empty, e:
            logging.warn("receive timeout");
            self.errors_response_timeout += 1
            return None





