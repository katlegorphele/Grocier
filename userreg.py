from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict

app = FastAPI()

# Secret key for JWT token
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB client
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["mydatabase"]
users_collection = db["users"]
shoppingLIst_collection = db['shopping_lists']


# Pydantic models for user input and token response
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserShoppingList(BaseModel):
    items : List

class ShoppingListInput(BaseModel):
    items: List[str]


# Function to create JWT token
def create_access_token(username: str, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from JWT Token
async def get_current_user(token:str = Depends(create_access_token)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401,detail='Invalid authentication token')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid authentication token')
    return username
        

# User registration endpoint
@app.post("/register/", response_model=Token)
async def register_user(user: User):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password
    hashed_password = pwd_context.hash(user.password)
    
    # Store user in MongoDB
    user_data = {"username": user.username, "password": hashed_password}
    await users_collection.insert_one(user_data)
    
    # Generate JWT token
    access_token = create_access_token(user.username, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# User login endpoint
@app.post("/login/", response_model=Token)
async def login_user(user: User):
    stored_user = await users_collection.find_one({"username": user.username})
    if not stored_user or not pwd_context.verify(user.password, stored_user["password"]):
        return
        # raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    
    # Generate JWT token
    access_token = create_access_token(user.username, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

#Shopping list endpoint
@app.post('/shopping_list/create')
async def create_shopping_list(shopping_list: ShoppingListInput, current_user: str = Depends(get_current_user)):
    if shopping_list is None:
        raise HTTPException(status_code=400, detail="Invalid shopping list data")
    
    # Get the user who is creating the shopping list
    user = await users_collection.find_one({"username": current_user})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    items = shopping_list.items
    
    # Add the user_id to the shopping list document
    await shoppingLIst_collection.insert_one({"user_id": user["_id"], "items": items})
    
    return {"message": "Shopping list created successfully"}


# Logout endpoint
@app.post("/logout/")
async def logout():
    # You might want to implement some logic to invalidate the token on the client side
    return {"message": "Logged out successfully"}



