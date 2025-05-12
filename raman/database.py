import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("ME_CONFIG_MONGODB_URL")
MONGO_DB = "raman"
MONGO_COLLECTION_BLOOD = "blood_glucose"
MONGO_COLLECTION_REFERENCE = "reference"

client: MongoClient = MongoClient(f'{os.environ["ME_CONFIG_MONGODB_URL"]}')
db = client.get_database(MONGO_DB)
collection_blood = db.get_collection(MONGO_COLLECTION_BLOOD)
collection_ref   = db.get_collection(MONGO_COLLECTION_REFERENCE)


def create_collection():
    """Create the collection"""
    # collection = db.get_collection(MONGO_BLOOD)
    collection_blood.create_index(["subject_id", "timestamp"], unique=True)
    collection_ref.create_index(["name", "timestamp"], unique=True)


def reset_collection():
    """Reset the collection"""
    collection_blood.drop()
    collection_blood.create_index(["subject_id", "timestamp"], unique=True)
    collection_ref.drop()
    collection_ref.create_index(["name", "timestamp"], unique=True)
