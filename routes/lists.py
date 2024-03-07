from fastapi import APIRouter, Depends, HTTPException
from models.shopping_list import ShoppingList
from models.user import User
from database.db import list_collection
from main import get_current_active_user
from bson.objectid import ObjectId

router = APIRouter()

@router.post('/lists', tags=["Lists"])
async def create_list(list: ShoppingList, current_user: User = Depends(get_current_active_user)):
    '''
    Allows the creation of a new shopping list
    '''
    result = list_collection.insert_one({"name":list.name, "items": list.items, "user_id": current_user.username})
    return {"id":str(result.inserted_id)}

@router.get("/lists",tags=["Lists"])
async def read_lists(current_user: User = Depends(get_current_active_user)):
    '''
    Returns all saved shopping lists
    '''
    lists = list_collection.find({"user_id": current_user.username})
    return {"lists":[{**list, "_id": str(list["_id"])} for list in lists]}

@router.put("/lists/{list_id}",tags=["Lists"])
async def update_list(list_id: str, list: ShoppingList, current_user: User = Depends(get_current_active_user)):
    '''
    Allows the updating of saved shopping lists
    '''
    result = list_collection.update_one({"_id": ObjectId(list_id), "user_id": current_user.username}, {"$set": {"name": list.name, "items": list.items}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List updated successfully"}

@router.delete("/lists/{list_id}",tags=["Lists"])
async def delete_list(list_id: str, current_user: User = Depends(get_current_active_user)):
    '''
    Allows the deletion of existing shopping lists
    '''
    result = list_collection.delete_one({"_id": ObjectId(list_id), "user_id": current_user.username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted successfully"}

