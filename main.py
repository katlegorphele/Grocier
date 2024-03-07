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


options = FirefoxOptions()
options.add_argument('--headless')

#Initialize Fastapi & Selenium
app = FastAPI()
# browser = webdriver.Firefox()
app.include_router(users.router)
app.include_router(lists.router)


@app.on_event('startup')
async def startup_event():
    global browser
    browser = webdriver.Firefox(options=options)

@app.on_event('shutdown')
async def shutdown_event():
    browser.quit()

@app.get("/",)
async def read_root():
    '''
    Returns information about the application and its features
    '''
    return {
        "app": "Grocier",
        "version": "1.0.0",
        "features": {
            "User Authentication": "Secure user authentication using OAuth2.",
            "List Management": "Allows users to create and manage their shopping lists.",
            "Item Search": "Searches for items in the user's shopping list across multiple sites (pnp, checkers, woolworths) and returns the prices.",
        }
    }

def extract_price(price_str):
    match = re.search(r'(\d+\.\d+)', price_str)
    if match:
        return float(match.group(1))
    return None
    


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
        pnp_results = siteparsers.search_pnp(browser, item)
        checkers_results = siteparsers.search_checkers(browser, item)
        woolies_results = siteparsers.search_woolworths(browser, item)

        # pnp_price = extract_price(pnp_results)
        # checkers_price = extract_price(checkers_results)
        # woolies_price = extract_price(woolies_results)

        results[item] = {
            "pnp": pnp_results,
            "checkers": checkers_results,
            "woolies": woolies_results
        }

    return results