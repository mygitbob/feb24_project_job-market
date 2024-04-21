import logging
import sys
from datetime import datetime

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
        logging.basicConfig(filename=log_file, level=level)
        with open(log_file, 'a'):
            logging.debug("-"*40)
            logging.debug(f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")} Starting ...")
    else:
        logging.basicConfig(stream=sys.stdout, level=level)
