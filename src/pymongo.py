import pymongo
import json

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

if __name__ == "__main__":
    main()


