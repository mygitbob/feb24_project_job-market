import init
from postgres_initdb import POSTGRES_DBNAME, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER
from postgres_queries import connect_db, get_data
from logger import logging
from mlmodel import train_model
def main():
    logging.debug("Get database entries")
    engine = connect_db(POSTGRES_USER, 
                        POSTGRES_PASSWORD,
                        POSTGRES_HOST,
                        POSTGRES_PORT,
                        POSTGRES_DBNAME)
    df = get_data(engine)
    logging.debug("Start model training")
    print(df.head())
    train_model(df)

if __name__ == "__main__":
    main()

    
    