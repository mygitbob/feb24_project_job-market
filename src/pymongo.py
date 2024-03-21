import pymongo
import json
import os

# MongoDB connection details
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
DATABASE_NAME = 'jobmarket'

# load JSON files from a directory
def load_json_files(directory):
    json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
    data = []
    for file in json_files:
        with open(os.path.join(directory, file), 'r') as f:
            data.extend(json.load(f))
    return data

# connect to MongoDB
def connect_to_mongodb(host, port):
    client = pymongo.MongoClient(host, port)
    return client

# create collections and insert data into MongoDB
def build_database(client, database_name, data_sources):
    db = client[database_name]
    for source, json_file in data_sources.items():
        collection_name = source.replace(' ', '_').lower() 
        collection = db[collection_name]
        data = load_json_files(json_file)
        collection.insert_many(data)
        print(f"Inserted {len(data)} documents into collection '{collection_name}'")

if __name__ == "__main__":
    # Specify the directory containing JSON files for each data source
    data_sources = {
        'Okjob': '/data/processed/raw_sample_data/okjob_raw.json',
        'Muse': '/data/processed/raw_sample_data/muse_job_entry_0.json',
        'Adzuna': '/data/processed/raw_sample_data/adzuna_job_entry_0.json'
        
    }

    # Connect to MongoDB
    client = connect_to_mongodb(MONGO_HOST, MONGO_PORT)

    # Build the database
    build_database(client, DATABASE_NAME, data_sources)

    # Close MongoDB connection
    client.close()
