import os
import csv
import json
from datetime import datetime
from constants import Constants
from logger import logging

def save_raw_api_data(fname, data, subdir = ''):
    """
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
    loads raw api data as json file list, if fname is empty then get all files in subdir
    returns filepath and content (json)
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

"""
def save_proccessed_data(to_save_list, subdir='', delete_files=False):
    
    files2delete = []
    path2save = os.path.join(Constants.PATH_DATA_PROCESSED, subdir)
    if not os.path.exists(path2save):
        os.mkdir(path2save)
    for json_dict, fname_raw in to_save_list:
        fout = os.path.basename(fname_raw).replace('_raw_', '_proccessed_')
        filepath = os.path.join(path2save, fout)
        with open(filepath, 'w') as f:
            json.dump(json_dict, f, indent=4)
        if delete_files:
            files2delete.append(fname_raw)
    if files2delete:
        remove_raw_api_data(files2delete)    
"""
def save_proccessed_data(data_to_save, source_file, subdir='', delete_source=False, write_json=True, Write_csv=True):
    """
    saves list of job entries (json format) in processed data folder
    can save as json or csv
    """
    path2save = os.path.join(Constants.PATH_DATA_PROCESSED, subdir)
    if not os.path.exists(path2save):
        os.mkdir(path2save)
    fout = os.path.basename(source_file).replace('_raw_', '_proccessed_')
    if write_json:
        json_filepath = os.path.join(path2save, fout)
        with open(json_filepath, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    if Write_csv:
        csv_filepath = os.path.join(path2save, fout).rsplit(".", maxsplit=1)[0] + ".csv"
        with open(csv_filepath, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = data_to_save[0].keys())
            writer.writeheader()
            writer.writerows(data_to_save)
    if delete_source:
        remove_raw_api_files([source_file])    

def remove_raw_api_files(files2delete):
    """
    deletes files in list files2delete
    """
    for to_delete in files2delete:
        try:
            os.remove(to_delete)
        except OSError as e:
            logging.error(f"helpers_io.py: remove_raw_api_data: error deleting file: {to_delete}")

if __name__ == "__main__":
    pass
    # TODO
    # create dummy json data
    # test save functions
    #res = load_raw_data()
    #print(len(res))
    #print(load_raw_data(fname="adzuna_joblist_all_entries.json"))
    #res = load_raw_api_data(subdir="muse.com")
    #print( [ ( i[0], len(i[1]) )  for i in res] )
    dummy = [{'eins':1,'zwei':2,'drei':3},{'eins':11,'zwei':22,'drei':33}]
    save_proccessed_data(dummy, "my.json.dummy.json", subdir='', delete_source=False, write_json=True, Write_csv=True)