import os
import sys
import psycopg2 as psy

from logger import setup_logging, logging

"""
setting variables from environement
in the environment has following variables have to be set:
    POSTGRES_DBNAME     name of the database inside postgres
    POSTGRES_USER       username to connect to postgres
    POSTGRES_PASSWORD   password of the user (see above)
    POSTGRES_HOST       network address of postgres
    POSTGRES_PORT       port of postgres
"""
    
POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME', '_UNKOWN_')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '_UNKOWN_')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '_UNKOWN_')
try:
    POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', '5432'))
except ValueError as ve:
    logging.error(f"{__file__}: init_db: port number must be an integer: {ve}")
    raise ValueError from ve 
LOGFILE = os.environ.get('LOGFILE', None)


# TODO check required env vars

__all__ = ['POSTGRES_DBNAME']

# setup logfile    
setup_logging(LOGFILE)


def connect_to_database(dbname=POSTGRES_DBNAME):
    """
    Connects to postgres databse, connection has to be closed after using
    Function does not handele Exceptions, these has to be handeled by the calling instance

    Args:
        TODO    
    Returns:
        conn : connection   = connection object to postgres        
        dbname : str        = name of databse, when we create a new database we have to connect to the postgres db first
    """
    try:
            conn = psy.connect(
            dbname=dbname,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
    except Exception as e:
        logging.error(f"{__file__}: can not connect to database: {e}")
        sys.exit(-1)
    logging.info(f"{__file__}: database connection established")
    return conn   
        
# test db connection
connect_to_database()
        
        
if __name__ == "__main__":
    print("dbname:", POSTGRES_DBNAME)
    print("user", POSTGRES_USER)
    print("password", POSTGRES_PASSWORD)
    print("host", POSTGRES_HOST)
    print("port", POSTGRES_PORT)