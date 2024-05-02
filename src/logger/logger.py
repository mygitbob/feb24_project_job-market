import logging
import sys
from datetime import datetime

def setup_logging(log_file=None, level=logging.DEBUG, reset = False):
    """
    Enables logging, when no log_file given prints on screen

    Args:
        log_file : str  = filepath, when empty use stdout
        level : str     = debug level
        reset : bool    = if True than a new log file will be created and the old one deleted
    Returns:
        None
    """

    if log_file:
        
        if reset:
            mode = 'w'
        else:
            mode = 'a'
            
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s', filename=log_file, level=level)
        
        with open(log_file, mode):
            logging.info("-"*40)
            logging.info(" Starting ...")
            
    else:
        logging.basicConfig(stream=sys.stdout, level=level)
