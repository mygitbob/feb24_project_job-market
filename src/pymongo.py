import pymongo
import json

# connect to MongoDB
client = pymongo.MongoClient(
    host="127.0.0.1",
    port = 27017
    )
db = client["jobmarket"]

# create collections variables for two datasource
okjobs_collection = db["okjobs"]
reed_collection = db["reed"]

#read json files
with open("/data/processed/row_sample_data/okjob_raw.json", "r") as okjobs_file:
    okjobs_data = json.load(okjobs_file)

with open("/data/processed/row_sample_data/reed_raw.json", "r") as reed_file:
    reed_data = json.load(reed_file)

# insert data into collections using unique id

for job in okjobs_data:
    if not okjobs_collection.find_one({"id": job["id"]}):
        okjobs_collection.insert_one(job)

for job in reed_data:
    if not reed_collection.find_one({"id": job["id"]}):
        reed_collection.insert_one(job)


