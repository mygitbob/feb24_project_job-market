import os
import my_secrets

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
    PATH_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # base path is parent directory of src folder
    PATH_DATA_RAW = os.path.join(PATH_BASE, "data/raw")
    PATH_DATA_PROCESSED = os.path.join(PATH_BASE, "data/processed")
    PATH_SRC = os.path.join(PATH_BASE, "src")

    # name of subfolder for both data/ raw AND data/proccessed
    DIR_NAME_MUSE = "muse.com"          
    DIR_NAME_OKJOB = "okjob.io"
    DIR_NAME_REED = "reed.co.uk"
    
    API_VERSION_REED = "1.0"
    
    SALARY_ENTRY_MUSE = "contents"
    KOWN_CURRENCY = ['$', '£' , '€']

    LOG_FILE = os.path.join(PATH_SRC, "log.txt")

    # TODO: move secrets to a safe place
    ADZUNA_APP_ID = my_secrets.ADZUNA_APP_ID
    ADZUNA_API_KEY = my_secrets.ADZUNA_API_KEY
    JOOBLE_API_KEY = my_secrets.JOOBLE_API_KEY
    OKJOB_API_KEY = my_secrets.OKJOB_API_KEY
    REED_API_KEY = my_secrets.REED_API_KEY

    BAD_RESPONSE = "Error - No Data received"

if __name__ == "__main__" :

    print("Project Constants:")
    print("Path Base:", Constants.PATH_BASE)
    print("Path Data Raw:", Constants.PATH_DATA_RAW)
    print("Path Data Processed:", Constants.PATH_DATA_PROCESSED)
    print("Path to log file:", Constants.LOG_FILE)
    print("my secrets Adzuna APi Key:", Constants.ADZUNA_API_KEY)
