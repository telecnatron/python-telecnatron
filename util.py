# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015 - 2016. http://telecnatron.com/
# $Id: $
# -----------------------------------------------------------------------------
import sys
import logging

def logging_config(level=logging.INFO):
    """
    Configure logging to use required standard format.
    See doc for LogRecord attributes: https://docs.python.org/2/library/logging.html#logging.Logger
    :param level: one of logging.DEBUG, logging.INFO etc
    """
    logging.basicConfig(format='LOG:%(levelname)s:%(asctime)s.%(msecs)d:%(filename)s:%(lineno)d: %(message)s', datefmt="%H%M%S", level=level)


def dict_valkey(diction, val):
    """
    Given passed dictionary reference, returns the first key found whose value is equal to val, 
    or None if no matching value.

    :param diction: the dictionary whose key is to be looked for 
    :type diction: reference to dictionary object
    :param val: reference to dictionary
    :returns: Reference to the dictionary's matching key object
    """
    for dkey, dval in diction.iteritems():
        if dval == val:
            return dkey
    return None
