#!/usr/bin/env python3

'''
Module to hold pydantic models for Shopping List
'''

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

#Pydantic Models


class ShoppingList(BaseModel):
    name: str
    items: List[str]


class Item(BaseModel):
    name: str

class Config:
    schema_extra = {
        "example": {
            "username": "johndoe",
            "email": "jdoe@mail.com",
            "full_name": "John Doe",
            "password": "password"
        }
    }
