import argparse
import init
import postgres_create as pc
import postgres_inserts as pi
from check_dataframe import check_dataframe, strip_capitalize_strings
from transform_reed import load_and_transform

from logger import logging

def main(command):
    if command == "setup":
        logging.debug(f"{__file__}: Starting database creation")
        pc.create_all(drop=True)
        logging.debug(f"{__file__}: Database creation finished, for errors see log above")
        
    if command == "transform":
        logging.debug(f"{__file__}: Starting transformation")
        # here we do the transformation
        logging.debug(f"{__file__}: Transformation finished")
        
        logging.debug(f"{__file__}: Uploading to database")
        import pandas as pd                     #TODO: replace with real code
        df = pd.DataFrame(pi.data_with_holes)   #TODO: replace with real code
        logging.debug(f"{__file__}: Check DataFrame")
        errors = check_dataframe(df)
        if errors:
            logging.error(f"{__file__}: DataFrame contains errors, insert abrted, errors: {errors}")
            raise Exception("DataFrame contains errors, insertion aborted") # TODO catch Exception (I guess we do more than one DataFrame in a loop)
        else:
            logging.debug(f"{__file__}: DataFrame check passed")
        logging.debug(f"{__file__}: Stripping and capitalizing strings in DataFrame")
        df = strip_capitalize_strings(df)
        logging.debug(f"{__file__}: Storing DataFrame in postgres")
        pi.store_dataframe(df, check_df=False)  # checked already before
        logging.debug(f"{__file__}: Database uploading finished")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data transformation tool that can be used to set up the required database(s) and for the data transformation and storage in the database ('setup' or 'transform')")
    parser.add_argument("command", choices=['setup', 'transform'], help="setup to create the database(s) or transform and save data ('setup' or 'transform')")
    
    args = parser.parse_args()
    main(args.command)