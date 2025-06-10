import os
from pymongo import MongoClient
from typing import Any, Dict
MONGO_URI = os.environ.get("ME_CONFIG_MONGODB_URL")
MONGO_DB = "raman"
MONGO_COLLECTION_BLOOD = "blood"
MONGO_COLLECTION_FINGER = "finger"
MONGO_COLLECTION_REFERENCE = "reference"

client:MongoClient[Dict[str, Any]] = MongoClient(f'{os.environ["ME_CONFIG_MONGODB_URL"]}')
db = client.get_database(MONGO_DB)
collection_finger = db.get_collection(MONGO_COLLECTION_FINGER)
collection_blood = db.get_collection(MONGO_COLLECTION_BLOOD)
collection_ref   = db.get_collection(MONGO_COLLECTION_REFERENCE)


def create_collection():
    """Create the collection"""
    # collection = db.get_collection(MONGO_BLOOD)
    collection_finger.create_index(["subject_id", "timestamp"], unique=True)
    collection_blood.create_index(["name", "timestamp"], unique=True)
    collection_ref.create_index(["name", "timestamp"], unique=True)


def reset_collection():
    """Reset the collection"""
    collection_finger.drop()
    collection_finger.create_index(["subject_id", "timestamp"], unique=True)
    collection_blood.drop()
    collection_blood.create_index(["name", "timestamp"], unique=True)
    collection_ref.drop()
    collection_ref.create_index(["name", "timestamp"], unique=True)
