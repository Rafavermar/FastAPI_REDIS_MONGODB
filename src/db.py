from pymongo import MongoClient
from fastapi import Depends


def get_mongo_client():
    client = MongoClient('mongodb://mongo:27017/')
    try:
        yield client
    finally:
        client.close()


def get_users_collection(client=Depends(get_mongo_client)):
    db = client['actividad4_db']
    collection = db['users']
    try:
        yield collection
    finally:
        pass  # No necesitamos cerrar nada aquí
