from fastapi import APIRouter
from pymongo import MongoClient
from bson.objectid import ObjectId
from models.user import UserInDB

client = MongoClient('mongodb://localhost:27017/')
db = client['grocier']
users_collection = db['users']
list_collection = db['lists']

router = APIRouter()

def get_user(username:str):
    user = users_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)
    
def get_list_from_db(list_id):
    list_doc = list_collection.find_one({"_id": ObjectId(list_id)}) 
    if list_doc:
        return list_doc["items"]
    return None

@router.get("/test_db_connection", tags=['Utilities'])
async def test_db_connection():
    '''
    Utility function to test the database connection
    '''
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        return {"message": "MongoDB connection successful"}
    except Exception as e:
        return {"message": "MongoDB connection failed", "error": str(e)}