import os
import glob
import pandas as pd
from logger import logging

def get_raw_data(folder_path):
    """
    Reads csv files from folder_path and retturns them as a list of DataFrames
    Args:
        folder_path : str           = path of folder to look for csv files
        delete  : bool              = flag if source files should be deleted after transformed into DataFrame
    Returns:
        res : zip object       = zip object with list of filenames and list of DataFrames from folder_path
    """
    dataframe_list = []
    filename_list = []
    for file_path in glob.glob(folder_path + '/*.csv'):

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logging.error(f"{__file__}: cant create dataframe for {file_path}: {e}")
        dataframe_list.append(df)
        filename_list.append(file_path)
    logging.debug(f"{__file__}: filenmes: {filename_list}")
    res = zip(filename_list, dataframe_list)
    return res
                    
def rm_raw_data(file_list):
    """
    Delete source files
    Args:
        file_list : list  = list of files to be deleted
    Returns:
        None
    """
    for csv_file_path in file_list:
        try:
            if csv_file_path.endswith('.csv'):
                    csv_directory, csv_file_name = os.path.split(csv_file_path)
                    json_file_path = os.path.join(csv_directory, csv_file_name.replace('.csv', '.json'))
                    if os.path.exists(json_file_path):
                        os.remove(json_file_path)
                        logging.debug(f"{__file__}: removed file: {json_file_path}")
                    os.remove(csv_file_path)
                    logging.debug(f"{__file__}: removed file: {csv_file_path}")
        except Exception as e:
            logging.error(f"{__file__}: error deleting file: {csv_file_path} : {e}")            
    

if __name__ == "__main__":
    zipper = get_raw_data("../../data/processed/muse.com/merged")
    for filepath, df in zipper:
        print(df)