import postgres_initdb
import os
from logger import setup_logging, logging

PATH_DATA_PROCESSED = os.environ.get('PATH_DATA_PROCESSED', None)
DIR_NAME_MUSE = os.environ.get('DIR_NAME_MUSE', None)
DIR_NAME_REED = os.environ.get('DIR_NAME_REED', None)
DIR_NAME_OKJOB = os.environ.get('DIR_NAME_OKJOB', None)

class InitError(Exception):
    """ Error is raised when the required environment variables are not set"""
    pass

LOGFILE = os.environ.get('LOGFILE', None)

env_vars = {
    "PATH_DATA_PROCESSED": PATH_DATA_PROCESSED,
    "DIR_NAME_MUSE": DIR_NAME_MUSE,
    "DIR_NAME_OKJOB": DIR_NAME_OKJOB,
    "DIR_NAME_REED": DIR_NAME_REED
}

# check env_vars
if not all(env_vars.values()):
    msg = f"All required environment variables must be set: {', '.join([f'{var_name}={var_value}' for var_name, var_value in env_vars.items()])}"
    logging.error(f"{__file__}: {msg}")
    raise EnvironmentError(msg)

# setup logfile    
setup_logging(LOGFILE)

if __name__ == "__main__":
    print("Environment variables:\n", env_vars)
