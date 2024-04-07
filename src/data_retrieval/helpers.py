import os
import sys
import csv
import json
from datetime import datetime

# project diretory
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# add to python path
sys.path.append(project_path)

from config.constants import Constants
from config.logger import logging, setup_logging

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
        with open(os.path.join(path2save, fname), 'w', encoding='utf-8') as file:
            logging.debug(f"helpers: save_raw_data: write json file: {fname}")
            file.write(data)
    elif isinstance(data, list):  
        with open(os.path.join(path2save, fname), 'w', encoding='utf-8') as file:
            logging.debug(f"helpers: save_raw_data: write json file: {fname}")
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
            with open(file, encoding='utf-8') as f:
                try:
                    result.append((file, json.load(f)))
                    logging.debug(f"helpers: load_raw_data: load json file: {file}")
                except Exception as e:
                    logging.error(f"helpers: load_raw_data: json load failed for file: {file}")
        return result
    else: 
        for file in os.listdir(path2load):
            file = os.path.join(path2load, file)
            if file.endswith("json") and os.path.getsize(file) > 0:
                with open(file, encoding='utf-8') as f:
                    try:
                        result.append((file, json.load(f)))
                        logging.debug(f"helpers: load_raw_data: load json file: {file}")
                    except Exception as e:
                        logging.error(f"helpers: load_raw_data: json load failed for file: {file}")
        return result


def save_processed_data(data_to_save, source_file, subdir='', delete_source=False, write_json=True, write_csv=True):
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
        logging.debug(f"helpers: save_processed_data: mkdir: {path2save}")
        os.mkdir(path2save)
    fout = os.path.basename(source_file).replace('_raw_', '_processed_')
    if write_json:
        json_filepath = os.path.join(path2save, fout)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            logging.debug(f"helpers: save_processed_data: write json: {json_filepath}")
            json.dump(data_to_save, f, indent=4)
    if write_csv:
        csv_filepath = os.path.join(path2save, fout).rsplit(".", maxsplit=1)[0] + ".csv"
        with open(csv_filepath, 'w', encoding='utf-8') as f:
            logging.debug(f"helpers: save_processed_data: write csv: {csv_filepath}")
            writer = csv.DictWriter(f, fieldnames = data_to_save[0].keys())
            writer.writeheader()
            writer.writerows(data_to_save)
    if delete_source:
        # remove all files in dir
        delete_all_files_in_directory_of_file(source_file)
        # remove_files([source_file])    

# TODO: description
def delete_all_files_in_directory_of_file(file_path):
    directory_path = os.path.dirname(file_path)

    if not os.path.isdir(directory_path):
        logging.error(f"helpers: delete_all_files_in_directory_of_file: cant get dir name: {file_path}")
        return
    
    file_list = os.listdir(directory_path)
    
    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            logging.debug(f"helpers: delete_all_files_in_directory_of_file: deleting file: {file_path}")
        else:
            logging.error(f"helpers: delete_all_files_in_directory_of_file: error deleting file: {file_path}")
    


def remove_files(files2delete):
    """
    Deletes files in list files2delete

    Args:
        files2delete: list[ filepath ]
    Returns:
        None
    """
    for to_delete in files2delete:
        try:
            logging.debug(f"helpers: remove_raw_api_data: deleting file: {to_delete}")
            os.remove(to_delete)
        except OSError as e:
            logging.error(f"helpers: remove_raw_api_data: error deleting file: {to_delete}")


def merge_files(folder, prefix, delete_source=False, name_add = ''):
    """
    Combines multiple files with the same prefix in data/processed or a subfolder of that into a single file
    BEWARE: dont merge the same files several times
    Args:
        folder : str                = folder for files to merge
        prefix : str                = prefix of files to merge
        name_add : str         = add this string to the filename
        delete_source : bool        = delete source files ?

    Returns:
        None
    """
    if prefix == '': 
        prefix = folder
    source_path = os.path.join(Constants.PATH_DATA_PROCESSED, folder)
    merged_json = []
    merged_csv = []
    files2delete = []

    if not os.path.exists(source_path):
        logging.debug(f"helpers: merge_files: make dir: {source_path}")
        os.mkdir(source_path)

    for file in os.listdir(source_path):
        if file.startswith(prefix):
            if file.endswith('.json'):
                with open(os.path.join(source_path, file), encoding='utf-8') as f:
                    logging.debug(f"helpers: merge_files: open json: {file}")
                    merged_json.extend(json.load(f))
                    if delete_source:
                        files2delete.append(os.path.join(source_path, file))
            elif file.endswith('.csv'):
                merged_csv.append(os.path.join(source_path, file))
                if delete_source:
                    files2delete.append(os.path.join(source_path, file))
    if name_add:
        prefix = prefix + f'.{name_add}'
    out_file = prefix + f".merged." + str(datetime.now().strftime("%Y-%m-%d_%H-%M"))
    

    # create new ouput dir because the files will be deleted after merge -> no double merging please
    if 'merged' not in os.listdir(source_path):
        os.mkdir(os.path.join(source_path, 'merged'))
    source_path = os.path.join(source_path, 'merged')
    if merged_json:
        jout_file = out_file + ".json"
        with open(os.path.join(source_path, jout_file), 'w', encoding='utf-8') as f:
            logging.debug(f"helpers: merge_files: write json: {jout_file}")
            json.dump(merged_json, f)

    if merged_csv:    
        cout_file = out_file + ".csv"
        with open(os.path.join(source_path, cout_file), 'w', newline='', encoding='utf-8') as outf:
            logging.debug(f"helpers: merge_files: write csv: {cout_file}")
            writer = csv.writer(outf)

            # write header only once
            with open(os.path.join(source_path, merged_csv[0]), 'r', newline='', encoding='utf-8') as inf:
                reader = csv.reader(inf)
                header = next(reader)
                writer.writerow(header)

            # skip 1st row, we already have the header
            for csv_file in merged_csv:
                with open(os.path.join(source_path, csv_file), 'r', newline='', encoding='utf-8') as inf:
                    reader = csv.reader(inf)
                    # skip header
                    next(reader)
                    for row in reader:
                        if row:             # no empty lines please
                            writer.writerow(row)

    if files2delete:
        remove_files(files2delete)

if __name__ == "__main__":
    setup_logging()
    #res = load_raw_data()
    #print(len(res))
    #print(load_raw_data(fname="adzuna_joblist_all_entries.json"))
    #res = load_raw_api_data(subdir="muse.com")
    #print( [ ( i[0], type(i[1]) )  for i in res] )
    #dummy = [{'eins':1,'zwei':2,'drei':3},{'eins':11,'zwei':22,'drei':33}]
    #save_processed_data(dummy, "my.json.dummy.json", subdir='', delete_source=False, write_json=True, write_csv=True)
    merge_files(Constants.DIR_NAME_MUSE, 'muse_proc', delete_source=True)