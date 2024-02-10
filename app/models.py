#!/usr/bin/env python3

'''
Base models
'''

from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    password: str

class GroceryList(BaseModel):
    owner: str
    items: str