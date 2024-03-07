#!/usr/bin/env python3

'''
Module to test authentication and auth in Fastapi
'''


from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException
import siteparsers
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from models.user import User
from database.db import client, get_list_from_db
from auth.auth import get_current_active_user
from routes import users,lists
import redis
import json

#API Metadata
description = """
Grocier API helps you manage your shopping lists efficiently. 🚀

## Shopping Lists

You can **create**, **read**, **update**, and **delete** shopping lists.

## Items

You can **search** for items and get their prices from various stores. The results are cached in Redis for faster subsequent searches.

## Users

You will be able to:

* **Register users**: New users can register by providing a username, email, and password.
* **Authenticate users**: Users can log in by providing their username and password. They will receive a token that they can use for authenticated requests.
* **Read users**: Get information about a user.
* **Update users**: Update the information of a user.
* **Delete users**: Delete a user from the system.

## Utilities

You can **test the database connection** and **test the Redis connection** to ensure that your system is working correctly.
"""

tags_metadata = [
    {
        "name": "Shopping Lists",
        "description": "Operations with shopping lists. The whole list of items that you can manage.",
    },
    {
        "name": "Items",
        "description": "Manage items. You can search for items and get their prices from various stores.",
    },
    {
        "name": "Users",
        "description": "Manage users. You can register, authenticate, read, update, and delete users.",
    },
    {
        "name": "Utilities",
        "description": "Utilities. You can test the database connection and test the Redis connection.",
    },
]


# Initialize Redis
r = redis.Redis(host='localhost', port=6379, db=0)


#Initialize Fastapi
app = FastAPI(
    name="Grocier",
    description=description,
    summary="Grocier API helps you manage your shopping lists efficiently",
    version="1.0.0",
    contact={
        "name": "Katlego R Phele",
        "url": "https://github.com/katlegorphele",
        "email": "katlegophele95@gmail.com"
    },
    license_info={
        "name":"MIT LICENSE",
        "identifier":"MIT",
    },
)

#Include the routers
app.include_router(users.router)
app.include_router(lists.router)


#Initialize a headless browser when the app starts
options = FirefoxOptions()
options.add_argument('--headless')

@app.on_event('startup')
async def startup_event():
    global browser
    browser = webdriver.Firefox(options=options)

# Close browser on server shutdown
@app.on_event('shutdown')
async def shutdown_event():
    browser.quit()

@app.get("/",)
async def read_root():
    '''
    Returns information about the application and its features
    '''
    return {"info": description}


@app.get("/test_db_connection", tags=['Utilities'])
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
    
@app.get('/test_redis_connection', tags=['Utilities'])
async def test_redis_connection():
    '''
    Utility function to test the redis connection
    '''
    try:
        r.ping()
        return {"message": "Redis connection successful"}
    except Exception as e:
        return {"message": "Redis connection failed", "error": str(e)}

@app.get("/search/{list_id}",response_model=Dict[str, Dict[str, Optional[str]]], tags=["Search"])
async def search_items(list_id:str, current_user: User = Depends(get_current_active_user)):
    '''
    Function to search for items in the shopping list
    '''
    # Fetch the list from the database
    items = get_list_from_db(list_id)
    if not items:
        raise HTTPException(
            status_code=404,
            detail="List not found",
        )
    
    results = {}
    for item in items:
        # Try get item from redis
        cached_result = r.get(item)
        if cached_result is not None:
            results[item] = json.loads(cached_result)
            continue

        # If the result is not in Redis, do the expensive operation
        pnp_results = siteparsers.search_pnp(browser, item)
        checkers_results = siteparsers.search_checkers(browser, item)
        woolies_results = siteparsers.search_woolworths(browser, item)


        results[item] = {
            "pnp": pnp_results,
            "checkers": checkers_results,
            "woolies": woolies_results
        }

        # Cache the result for one hour
        r.set(item, json.dumps(results[item]), ex=3600)

    return results

def extract_price(price_str):
    match = re.search(r'(\d+\.\d+)', price_str)
    if match:
        return float(match.group(1))
    return None