import postgres_initdb
import os
from logger import setup_logging, logging

PATH_MODEL = os.environ.get('PATH_MODEL', None)

class InitError(Exception):
    """ Error is raised when the required environment variables are not set"""
    pass

LOGFILE = os.environ.get('LOGFILE', None)

env_vars = {
    "PATH_MODEL": PATH_MODEL
}

# check env_vars
if not all(env_vars.values()):
    msg = f"All required environment variables must be set: {', '.join([f'{var_name}={var_value}' for var_name, var_value in env_vars.items()])}"
    logging.error(msg)
    raise EnvironmentError(msg)

# setup logfile    
setup_logging(LOGFILE)

if __name__ == "__main__":
    print("Environment variables:\n", env_vars)