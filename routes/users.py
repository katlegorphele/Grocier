#!/usr/bin/env python3

'''
Module to handle user routes
'''

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from models.user import Token,User, UserBase, UserCreate
from database.db import users_collection
from auth.auth import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user, authenticate_user, create_access_token, get_password_hash

router = APIRouter()

@router.post("/token", response_model=Token,tags=["Users"])
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

@router.get('/users/me', response_model=User, tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    '''
    Returns the current user
    '''
    return current_user

@router.post('/register', response_model=UserBase,tags=["Users"])
async def register(user: UserCreate):
    '''
    Allows users to register
    '''
    hashed_password = get_password_hash(user.password)
    result = users_collection.insert_one({"username":user.username,"email":user.email, "full_name": user.full_name, "hashed_password": hashed_password, "disbaled": False})
    return {"username": user.username, "email":user.email, "full_name":user.full_name}
