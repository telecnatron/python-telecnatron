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
import sys
import logging

def logging_config(level=logging.INFO):
    """Configure logging to use required standard format."""
    # see doc for LogRecord attributes: https://docs.python.org/2/library/logging.html#logging.Logger
    logging.basicConfig(format='LOG:%(levelname)s:%(asctime)s.%(msecs)d:%(filename)s:%(lineno)d: %(message)s', datefmt="%H%M%S", level=level)


def dict_valkey(diction, val):
    """Given passed dictionary reference, returns the first key found whose value is equal to val, or None of matching value"""
    for dkey, dval in diction.iteritems():
        if dval == val:
            return dkey
    return None
