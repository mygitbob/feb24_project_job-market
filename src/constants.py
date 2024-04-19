import os
import sys

# project src diretory
project_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# add to python path
sys.path.append(project_src_path)

import config.my_secrets as my_secrets

class CMeta(type):
    """
    DOTO: ensure that members of class Constants
    cant be altered
    """
    pass


class Constants(metaclass=CMeta):
    """
    defines all constants for the project
    """
    # data directories
    PATH_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    PATH_DATA_RAW = os.path.join(PATH_BASE, "data", "raw")
    PATH_DATA_PROCESSED = os.path.join(PATH_BASE, "data", "processed")
    PATH_SRC = os.path.join(PATH_BASE, "src")

    LOG_FILE = os.path.join(PATH_BASE, "log.txt")
    
    # name of subfolder of data sources for both data/ raw AND data/proccessed
    DIR_NAME_MUSE = "muse.com"
    DIR_NAME_OKJOB = "okjob.io"
    DIR_NAME_REED = "reed.co.uk"

    API_VERSION_REED = "1.0"

    # API Keys
    ADZUNA_APP_ID = my_secrets.ADZUNA_APP_ID
    ADZUNA_API_KEY = my_secrets.ADZUNA_API_KEY
    JOOBLE_API_KEY = my_secrets.JOOBLE_API_KEY
    OKJOB_API_KEY = my_secrets.OKJOB_API_KEY
    REED_API_KEY = my_secrets.REED_API_KEY

    # Postgres Config
    POSTGRES_CONTAINERNAME = "jobmarket_sql_container"
    POSTGRES_DBNAME = "jobmarket"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = my_secrets.POSTGRES_PASSWORD
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5432

    # Misc, not used yet
    BAD_RESPONSE = "Error - No Data received"
    SALARY_ENTRY_MUSE = "contents"
    KNOWN_CURRENCY = ['$', '£', '€']

if __name__ == "__main__":

    print("Project Constants:")
    print("Path Base:", Constants.PATH_BASE)
    print("Path Data Raw:", Constants.PATH_DATA_RAW)
    print("Path Data Processed:", Constants.PATH_DATA_PROCESSED)
    print("Path to log file:", Constants.LOG_FILE)
    print("my secrets Adzuna APi Key:", Constants.ADZUNA_API_KEY)
    print("postgres password:", Constants.POSTGRES_PASSWORD)
