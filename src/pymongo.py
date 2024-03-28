import pymongo
import json
import pandas as pd
from sqlalchemy import create_engine

# connect to MongoDB
def connect_to_mongo(host, port, db_name):
    client = pymongo.MongoClient(host=host, port=port)
    db = client[db_name]
    return db
def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def insert_data_into_collection(collection, data):
    for item in data:
        if not collection.find_one({"id": item["id"]}):
            collection.insert_one(item)


#### Function to transform JSON data to DataFrame #####
def transform_to_df(collection, source):
    data = list(collection.find())
    if source == 'okjob':
        df = pd.DataFrame(data)
        df = df[['Job-Title', 'Location', 'Salary-Min', 'Salary-Max']]
        df.columns = ['Job_Title', 'Location', 'Min_Salary', 'Max_Salary']
        df['Currency'] = 'USD'  # okjob offers from US
    elif source == 'reed':
        df = pd.DataFrame(data)
        df = df[['jobTitle', 'locationName', 'minimumSalary', 'maximumSalary', 'currency']]
        df.columns = ['Job_Title', 'Location', 'Min_Salary', 'Max_Salary', 'Currency']
    return df

#### Function to store DataFrame in a relational database ####
def store_in_db(df, table_name, db_string):
    engine = create_engine(db_string)
    df.to_sql(table_name, engine, if_exists='replace', index=False)


def main():
    # Connect to MongoDB
    db = connect_to_mongo("127.0.0.1", 27017, "jobmarket")

    # Create collections variables for two data sources
    okjobs_collection = db["okjobs"]
    reed_collection = db["reed"]

    # Read JSON files
    okjobs_data = read_json_file("/data/processed/row_sample_data/okjob_raw.json")
    reed_data = read_json_file("/data/processed/row_sample_data/reed_raw.json")

    # Insert data into collections using unique id
    insert_data_into_collection(okjobs_collection, okjobs_data)
    insert_data_into_collection(reed_collection, reed_data)

     # Transform JSON data to DataFrame
    okjobs_df = transform_to_df(okjobs_collection, 'okjob')
    reed_df = transform_to_df(reed_collection, 'reed')

    # Store DataFrames in a relational database
    #postgres username: postgres password i set: 1221
    db_string = "postgresql://postgres:1221@localhost:5432/jobs"  # Replace with your actual DB string
    store_in_db(okjobs_df, 'okjobs_table', db_string)
    store_in_db(reed_df, 'reed_table', db_string)


if __name__ == "__main__":
    main()


# command to install postgre (mac os. ubuntu vm)
# sudo apt install postgresql-client-common
# sudo apt-get update
# sudo apt-get install postgresql postgresql-contrib



    
