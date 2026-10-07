import os
import json

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)


_client = None


def get_client():
    global _client

    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000
        )

    return _client


def get_db(db_name="nosql_labs"):
    client = get_client()
    return client[db_name]


def reset_collection(db_name, collection_name):
    db = get_db(db_name)

    if collection_name in db.list_collection_names():
        db[collection_name].drop()

    return db[collection_name]


def check_connection():
    try:
        client = get_client()

        client.admin.command("ping")

        return {
            "connected": True,
            "message": "MongoDB connection successful"
        }

    except PyMongoError as e:

        return {
            "connected": False,
            "message": str(e)
        }


def banner(message):
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)


def print_json(data):
    print(
        json.dumps(
            data,
            indent=4,
            default=str
        )
    )