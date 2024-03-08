import logging

def setup_logging(log_file):
    if log_file != 'stdout':
        with open(log_file, 'w'): pass # reset log
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
