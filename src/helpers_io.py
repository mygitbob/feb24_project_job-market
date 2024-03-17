import os
import csv
import json
from constants import Constants
from logger import logging, setup_logging

def save_raw_api_data(fname, data, subdir = ''):
    """
    Save result of api data as json file

    Args:
        fname : str                 = name of the file to save
        data : str | list [ str ]   = json dict as string or list of them
        subdir (optional) : str     = subfolder in data/raw, will be created if it does not exist
    
    Returns:
        None
    """
    path2save = os.path.join(Constants.PATH_DATA_RAW, subdir)
    fname = fname.replace(' ', '_')
    if not os.path.exists(path2save):
        os.mkdir(path2save)
    if isinstance(data, str):  
        with open(os.path.join(path2save, fname), 'w') as file:
            logging.debug(f"save_raw_data: write data: {fname}")
            file.write(data)
    elif isinstance(data, list):  
        with open(os.path.join(path2save, fname), 'w') as file:
            logging.debug(f"save_raw_data: write data: {fname}")
            file.write('[')            # multiple jsons have to be in an array
            for i, item in enumerate(data):
                file.write(item)
                if i < len(data) - 1:  # multiple jsons must be separated by ,
                    file.write(',')
                else:
                    file.write(']\n') 
    else:
        raise ValueError("Raw data to write must be string or list of strings")

def load_raw_api_data(subdir = '', fname=''):
    """
    Loads raw api data of all files in folder
    Returns a list of tupels that contain the filename of the source and the content

    Args:
        subdir (optional) : str     = name of subfolder of data/raw
        fname (optional) : str      = name of a specific file, when not empty only load the conent of this file

    Returns:
         list of tuples: [ (filepath : str, json_data: dict) ]
    """
    path2load = os.path.join(Constants.PATH_DATA_RAW, subdir)
    result = []
    if fname != '':
        file = os.path.join(path2load, fname)
        if file.endswith("json") and os.path.getsize(file) > 0:
            with open(file) as f:
                try:
                    result.append((file, json.load(f)))
                except Exception as e:
                    logging.error(f"load_raw_data: json load failed for file: {file}")
        return result
    else: 
        for file in os.listdir(path2load):
            file = os.path.join(path2load, file)
            if file.endswith("json") and os.path.getsize(file) > 0:
                with open(file) as f:
                    try:
                        result.append((file, json.load(f)))
                    except Exception as e:
                        logging.error(f"load_raw_data: json load failed for file: {file}")
        return result


def save_proccessed_data(data_to_save, source_file, subdir='', delete_source=False, write_json=True, write_csv=True):
    """
    Saves list of job entries (json format) in data/processed
    Can save data as json or csv

    Args:
        data_to_save : list [ dict ]       = json data of one source file
        source_file : str                  = filepath of json source file
        subdir (optional) : str            = name of subfolder of data/processed
        delete_source (optional) : bool    = should source file to be deleted ?       
        write_json (optional) : bool       = write file as json ?
        write_csv (optional) : bool        = write file as csv ?

    Returns:
        None
    """
    path2save = os.path.join(Constants.PATH_DATA_PROCESSED, subdir)
    if not os.path.exists(path2save):
        os.mkdir(path2save)
    fout = os.path.basename(source_file).replace('_raw_', '_proccessed_')
    if write_json:
        json_filepath = os.path.join(path2save, fout)
        with open(json_filepath, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    if write_csv:
        csv_filepath = os.path.join(path2save, fout).rsplit(".", maxsplit=1)[0] + ".csv"
        with open(csv_filepath, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = data_to_save[0].keys())
            writer.writeheader()
            writer.writerows(data_to_save)
    if delete_source:
        remove_raw_api_files([source_file])    

def remove_raw_api_files(files2delete):
    """
    Deletes files in list files2delete

    Args:
        files2delete: list[ filepath ]
    Returns:
        None
    """
    for to_delete in files2delete:
        try:
            os.remove(to_delete)
        except OSError as e:
            logging.error(f"helpers_io.py: remove_raw_api_data: error deleting file: {to_delete}")

if __name__ == "__main__":
    setup_logging()
    #res = load_raw_data()
    #print(len(res))
    #print(load_raw_data(fname="adzuna_joblist_all_entries.json"))
    #res = load_raw_api_data(subdir="muse.com")
    #print( [ ( i[0], type(i[1]) )  for i in res] )
    #dummy = [{'eins':1,'zwei':2,'drei':3},{'eins':11,'zwei':22,'drei':33}]
    #save_proccessed_data(dummy, "my.json.dummy.json", subdir='', delete_source=False, write_json=True, write_csv=True)