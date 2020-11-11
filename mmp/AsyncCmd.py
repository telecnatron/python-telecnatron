# ------------------------------------------------------------------------------
# Copyright 2020 Stephen Stebbing. telecnatron.com
#
#    Licensed under the Telecnatron License, Version 1.0 (the “License”);
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://telecnatron.com/software/licenses/
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an “AS IS” BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ------------------------------------------------------------------------------
#/**
# * @file   AsyncCmd.py
# * @author steves
# * @date   2017/02/22 00:56:10
# * 
# * @brief  
# * 
# */
import logging;
import Queue;
from MMP import *;


class CmdResponseMsg(MMPMsg):
    """ """
    def __init__(self):
        """ """
        MMPMsg.__init__(self)
        self.cmd = 0;
        self.status = 0;

    def __str__(self):
        """ """
        return "cmd: {}, status: {}: {}".format(self.cmd, self.status, MMPMsg.__str__(self));
        

class AsyncCmd(MMP):
    """ """

    # message FLAGS that we recognise
    FLAGS_ASYNC = 0x02
    FLAGS_CMD   = 0x01


    def __init__(self, transport=None):
        """ """
        MMP.__init__(self, transport);
        # init queue for async messages
        self.asyncq = Queue.Queue(maxsize=16);
        # init queue for cmd messages
        self.cmdq = Queue.Queue(maxsize=1);
        # keep track of number of messages received
        self.num_async = 0;
        self.num_cmd = 0;
        self.num_responses = 0;
        self.errors_unrecognised_msg = 0
        self.errors_invalid_cmd_response = 0
        self.errors_response_timeout = 0


    def handleMsg(self, msg):
        """ """
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



    def sendReceiveCmd(self, cmd, msgData, timeoutSec = 0.5):
        """ """
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





