import logging
import sys
from datetime import date

def setup_logging(log_file=None, level=logging.DEBUG, reset =True):
    """
    Enables logging, when no log_file given prints on screen
    Deletes old log file if same filename/path is given

    Args:
        log_file : str  = filepath, when empty use stdout
        level : str     = debug level

    Returns:
        None
    """
    if log_file:
        with open(log_file, 'a'):
            pass  # reset log
        logging.basicConfig(filename=log_file, level=level)
        logging.debug("-"*40)
        logging.debug(f"{date.today()} Starting ...")
    else:
        logging.basicConfig(stream=sys.stdout, level=level)
