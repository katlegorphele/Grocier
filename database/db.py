from pymongo import MongoClient
from bson.objectid import ObjectId
from models import UserInDB

client = MongoClient('mongodb://localhost:27017/')
db = client['grocier']
users_collection = db['users']
list_collection = db['lists']

def get_user(username:str):
    user = users_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)