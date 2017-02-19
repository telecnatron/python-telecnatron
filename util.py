# -----------------------------------------------------------------------------
# Copyright Stephen Stebbing 2015 - 2016. http://telecnatron.com/
# $Id: $
# -----------------------------------------------------------------------------
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
