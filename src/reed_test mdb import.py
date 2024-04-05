"""
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
# mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
#
# print(mongo_user, mongo_password)


def insert_json_files_to_mongodb(folder_path, collection_name):
    # MongoDB credentials and connection string
    mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    mongo_host = 'localhost'
    mongo_port = '27017'
    mongo_db = 'raw_data'
    connection_string = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/'

    # Connect to MongoDB with authentication
    client = MongoClient(connection_string)
    db = client[mongo_db]
    collection = db[collection_name]

    # Counters for inserted and skipped entries
    inserted_count = 0
    skipped_count = 0

    # Iterate through all JSON files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)

                entry_counter = 0  # Initialize entry counter
                # Ensure the data is a list of documents
                if isinstance(data, list):
                    for entry in data:

                        # Check if entry with same ID already exists in collection
                        if not collection.find_one({'id': entry['id']}):

                            # Insert entry if ID doesn't exist
                            collection.insert_one(entry)
                            inserted_count += 1
                        else:
                            skipped_count += 1
                        # entry_counter += 1  # Increment counter for each processed entry
                        # if entry_counter >= 30:  # Check if 10 entries have been processed
                        #     break  # Exit the loop after processing 10 entries

                    print(f"Data imported successfully. Documents inserted: {inserted_count}")
                else:
                    print("The provided JSON file does not contain a list of documents.")
    return inserted_count, skipped_count


# Example usage
folder_path = 'raw_imports/reed'
collection_name = 'reed_test'
inserted, skipped = insert_json_files_to_mongodb(folder_path, collection_name)
print(f"Inserted entries: {inserted}, Skipped entries: {skipped}")
"""

################################## Insert in bulk then delete duplicates ##################################

import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def insert_json_files_to_mongodb(folder_path, collection_name):
    # MongoDB credentials and connection string
    mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    mongo_host = 'localhost'
    mongo_port = '27017'
    mongo_db = 'raw_data'
    connection_string = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/'

    # Connect to MongoDB with authentication
    client = MongoClient(connection_string)
    db = client[mongo_db]
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

def remove_duplicates(mongo_db, collection_name, connection_string):
    client = MongoClient(connection_string)
    db = client[mongo_db]
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
folder_path = 'raw_imports/okjob'
collection_name = 'okjob_test'

# MongoDB credentials and connection string
mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
mongo_password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
mongo_host = 'localhost'
mongo_port = '27017'
mongo_db = 'raw_data'
connection_string = f'mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/'

inserted, skipped = insert_json_files_to_mongodb(folder_path, collection_name)
print(f"Inserted entries: {inserted}, Skipped entries: {skipped}")

# Remove duplicates after insertion
remove_duplicates(mongo_db, collection_name, connection_string)


