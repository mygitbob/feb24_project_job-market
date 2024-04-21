import os
from logger import setup_logging, logging

PATH_DATA_RAW = os.environ.get('PATH_DATA_RAW', None)
PATH_DATA_PROCESSED = os.environ.get('PATH_DATA_PROCESSED', None)
DIR_NAME_MUSE = os.environ.get('DIR_NAME_MUSE', None)
KNOWN_CURRENCY = os.environ.get('KNOWN_CURRENCY', None)
DIR_NAME_OKJOB = os.environ.get('DIR_NAME_OKJOB', None)
OKJOB_API_KEY = os.environ.get('OKJOB_API_KEY', None)
DIR_NAME_REED = os.environ.get('DIR_NAME_REED', None)
API_VERSION_REED = os.environ.get('API_VERSION_REED', None)
REED_API_KEY = os.environ.get('REED_API_KEY', None)

LOGFILE = os.environ.get('LOGFILE', None)


class InitError(Exception):
    """ Error is raised when the required environment variables are not set"""
    pass

# setup logfile    
setup_logging(LOGFILE)

env_vars = {
    "PATH_DATA_RAW": PATH_DATA_RAW,
    "PATH_DATA_PROCESSED": PATH_DATA_PROCESSED,
    "DIR_NAME_MUSE": DIR_NAME_MUSE,
    "KNOWN_CURRENCY": KNOWN_CURRENCY,
    "DIR_NAME_OKJOB": DIR_NAME_OKJOB,
    "OKJOB_API_KEY": OKJOB_API_KEY,
    "DIR_NAME_REED": DIR_NAME_REED,
    "API_VERSION_REED": API_VERSION_REED,
    "REED_API_KEY": REED_API_KEY
}

# check env_vars
if not all(env_vars.values()):
    msg = f"All required environment variables must be set: {', '.join([f'{var_name}={var_value}' for var_name, var_value in env_vars.items()])}"
    logging.error(f"{__file__}: {msg}")
    raise EnvironmentError(msg)


__all__ = ['[PATH_DATA_RAW', 'PATH_DATA_PROCESSED', 'DIR_NAME_MUSE', 'KNOWN_CURRENCY', 'DIR_NAME_OKJOB', 'OKJOB_API_KEY', 'DIR_NAME_REED', 'API_VERSION_REED', 'REED_API_KEY']

if __name__ == "__main__":
    print("Environment variables:\n", env_vars)