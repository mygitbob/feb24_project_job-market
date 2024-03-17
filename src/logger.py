import logging
import sys

def setup_logging(log_file=None, level=logging.DEBUG):
    """
    Enables logging and deletes resets logfile 

    Args:
        log_file : str  = filepath, when empty use stdout
        level : str ?   = debug level

    Returns:
        None
    """
    if log_file:
        with open(log_file, 'w'): pass # reset log
        logging.basicConfig(filename=log_file, level=level)
    else:
        logging.basicConfig(stream=sys.stdout, level=level)
