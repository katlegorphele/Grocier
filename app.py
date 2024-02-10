#!/usr/bin/env python3

'''
This file will be used as a mock up
of the final application
'''

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Connect to Mongo
client = MongoClient('mongodb://localhost:27017/')
db = client['grocier']
collection = db['groceries']

# DEfine MongoDB doc model for list
class GroceryList(BaseModel):
    items: list[str]

def get_grocery_list():
    grocery_list = []
    print("Enter your grocery items (type 'done' when finished):")
    while True:
        item = input('Enter item: ')
        if item.lower() == 'done':
            break
        grocery_list.append(item)
    return grocery_list

@app.get('/')
async def root():
    return {"message": "Welcome to Grocier API"}

# Route to recieve grocery list
@app.post('/grocery_list')
async def create_grocery_list(grocery_list: GroceryList):
    '''
    Create new grocery list and save it to Mongo
    '''
    g_items = grocery_list.items

    try:
        result = collection.insert_one({'items': grocery_list.items})
        return {"message":"Grocery list was successfully created", "id":str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)