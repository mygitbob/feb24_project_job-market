import init
import postgres_create as pc
import postgres_inserts as pi
from check_dataframe import check_dataframe, strip_capitalize_strings
from transform_reed import load_and_transform

from logger import logging

def main():
    
    # here we do the transformation
    logging.debug(f"{__file__}: Starting reed data processing")
    reed = load_and_transform()
    logging.debug(f"{__file__}: Reed finished")
    
    
if __name__ == "__main__":
    main()