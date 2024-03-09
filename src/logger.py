import logging
import sys

def setup_logging(log_file=sys.stdout, level=logging.DEBUG):
    if log_file != sys.stdout:
        with open(log_file, 'w'): pass # reset log
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
