import os

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

    LOG_FILE = os.path.join(PATH_SRC, "log.txt")

    # TODO: move secrets to a safe place
    ADZUNA_APP_ID = "fb3d1b6c"
    ADZUNA_API_KEY = "d1999430f1b272b9af611b798e8b0789"
    JOOBLE_API_KEY = "b056f9bf-136f-4fd5-8721-6fdc0d4453bc"
    OKJOB_API_KEY = "AIzaSyDErRezqW2klWRYKwQkzuOIMGJ5AeD5GSY"

    API_JOBLIST = ["adzuna", "muse", "jooble"]
    BAD_RESPONSE = "Error - No Data received"

class HTTPMethod():
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


if __name__ == "__main__" :

    print("Project Constants:")
    print("Path Base:", Constants.PATH_BASE)
    print("Path Data Raw:", Constants.PATH_DATA_RAW)
    print("Path Data Processed:", Constants.PATH_DATA_PROCESSED)
    print("Path to log file:", Constants.LOG_FILE)
