from postgres_initdb import POSTGRES_DBNAME, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER
import glob
import os
from joblib import load
from postgres_queries import connect_db

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

# connect to database
database_connection = connect_db(
            db_user=POSTGRES_USER,
            db_password=POSTGRES_PASSWORD,
            db_host=POSTGRES_HOST,
            db_port=POSTGRES_PORT,
            db_name=POSTGRES_DBNAME
)

# load models
os.chdir(PATH_MODEL)

pattern_min = "*_min_salary.latest.joblib"
pattern_max = "*_max_salary.latest.joblib"

match_min = glob.glob(pattern_min)
match_max = glob.glob(pattern_max)

if match_min and match_max:
    path_min = match_min[0]
    path_max = match_max[0]
    
    model_min = load(path_min)
    model_max = load(path_max)
    logging.info(f"{__file__}: models loaded")
else:
    msg = f"Can´t load models: {PATH_MODEL}"
    logging.error(msg)
    raise Exception(msg)


if __name__ == "__main__":
    print("Environment variables:\n", env_vars)