import postgres_initdb
import os
from logger import setup_logging


LOGFILE = os.environ.get('LOGFILE', None)

# setup logfile    
setup_logging(LOGFILE)
