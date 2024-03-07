#!/usr/bin/env python3

'''
Module to test authentication and auth in Fastapi
'''

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson.objectid import ObjectId
import siteparsers
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from models.user import Token,TokenData,User,UserInDB, UserBase, UserCreate
from models.shopping_list import ShoppingList, Item, Config
from database.db import users_collection, list_collection, get_user,client


options = FirefoxOptions()
options.add_argument('--headless')


SECRET_KEY = "9519b88e04d4b9d5ebb24484918c580a035d246a05795e8be0e4c3c2c2692a26"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


#Initialize Fastapi & Selenium
app = FastAPI()
# browser = webdriver.Firefox()


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


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username:str):
    user = users_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)
    
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not calidate credentials',
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
    
@app.post("/token", response_model=Token,tags=["Users"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    Function to generate an access token to login and authenticate user
    '''
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate":"Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub":user.username}, expires_delta=access_token_expires
    )
    return {"access_token":access_token, "token_type":"bearer"}

@app.get('/users/me', response_model=User, tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    '''
    Returns the current user
    '''
    return current_user

@app.post('/lists', tags=["Lists"])
async def create_list(list: ShoppingList, current_user: User = Depends(get_current_active_user)):
    '''
    Allows the creation of a new shopping list
    '''
    result = list_collection.insert_one({"name":list.name, "items": list.items, "user_id": current_user.username})
    return {"id":str(result.inserted_id)}

@app.get("/lists",tags=["Lists"])
async def read_lists(current_user: User = Depends(get_current_active_user)):
    '''
    Returns all saved shopping lists
    '''
    lists = list_collection.find({"user_id": current_user.username})
    return {"lists":[{**list, "_id": str(list["_id"])} for list in lists]}

@app.put("/lists/{list_id}",tags=["Lists"])
async def update_list(list_id: str, list: ShoppingList, current_user: User = Depends(get_current_active_user)):
    '''
    Allows the updating of saved shopping lists
    '''
    result = list_collection.update_one({"_id": ObjectId(list_id), "user_id": current_user.username}, {"$set": {"name": list.name, "items": list.items}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List updated successfully"}

@app.delete("/lists/{list_id}",tags=["Lists"])
async def delete_list(list_id: str, current_user: User = Depends(get_current_active_user)):
    '''
    Allows the deletion of existing shopping lists
    '''
    result = list_collection.delete_one({"_id": ObjectId(list_id), "user_id": current_user.username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted successfully"}

@app.post('/register', response_model=UserBase,tags=["Users"])
async def register(user: UserCreate):
    '''
    Allows users to register
    '''
    hashed_password = get_password_hash(user.password)
    result = users_collection.insert_one({"username":user.username,"email":user.email, "full_name": user.full_name, "hashed_password": hashed_password, "disbaled": False})
    return {"username": user.username, "email":user.email, "full_name":user.full_name}

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
    
def get_list_from_db(list_id):
    list_doc = list_collection.find_one({"_id": ObjectId(list_id)}) 
    if list_doc:
        return list_doc["items"]
    return None

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