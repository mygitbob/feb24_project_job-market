import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB credentials and connection string
mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
mongo_host = 'localhost'
mongo_port = '27017'
mongo_db = 'mdb_raw_data'
connection_string = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/'

# Global MongoDB client
client = MongoClient(connection_string)
db = client[mongo_db]

# Explicitly create collections
collections = ['muse_cltn', 'okjob_cltn', 'reed_cltn']
for coll_name in collections:
    if coll_name not in db.list_collection_names():
        db.create_collection(coll_name)

def insert_json_files_to_mongodb(folder_path, collection_name):
    collection = db[collection_name]

    # Counter for inserted entries
    inserted_count = 0

    # Iterate through all JSON files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)

                if isinstance(data, list):
                    # Change 'id' to 'sourceId' before insertion
                    for entry in data:
                        entry['sourceId'] = entry.pop('id')

                    # Insert all entries without checking for duplicates
                    result = collection.insert_many(data)
                    inserted_count += len(result.inserted_ids)

                    print(f"Data imported successfully. Documents inserted: {inserted_count}")
                else:
                    print("The provided JSON file does not contain a list of documents.")

    return inserted_count

def remove_duplicates(collection_name):
    collection = db[collection_name]

    # Aggregation pipeline to identify duplicates by 'sourceId' (excluding the first occurrence)
    pipeline = [
        {'$group': {'_id': '$sourceId', 'duplicateIds': {'$addToSet': '$_id'}, 'count': {'$sum': 1}}},
        {'$match': {'count': {'$gt': 1}}}
    ]
    duplicates = collection.aggregate(pipeline)

    # Counter for deleted duplicates
    deleted_count = 0

    for doc in duplicates:
        # Skip the first occurrence and delete the rest
        duplicate_ids = doc['duplicateIds'][1:]  # Exclude the first ID from deletion
        delete_result = collection.delete_many({'_id': {'$in': duplicate_ids}})
        deleted_count += delete_result.deleted_count

    print(f"Removed {deleted_count} duplicate documents.")

# Example usage
folder_paths = ['raw_imports/muse', 'raw_imports/okjob', 'raw_imports/reed']
collection_names = ['muse_cltn', 'okjob_cltn', 'reed_cltn']

for path, colltn in zip(folder_paths, collection_names):
    inserted = insert_json_files_to_mongodb(path, colltn)
    print(f"Inserted entries: {inserted}")

    # Remove duplicates after insertion
    remove_duplicates(colltn)
