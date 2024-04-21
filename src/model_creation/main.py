import init
from postgres_queries import connect_db, get_data
from logger import logging
from mlmodel import train_model
def main():
    logging.debug(f"{__file__}: Get databse entries")
    engine = connect_db(POSTGRES_USER, 
                        POSTGRES_PASSWORD,
                        POSTGRES_HOST,
                        POSTGRES_PORT,
                        POSTGRES_DBNAME)
    df = get_data(engine)
    logging.debug(f"{__file__}: Start model training")
    

if __name__ == "__main__":
    main()

    
    