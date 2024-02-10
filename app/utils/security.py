#!/usr/bin/env python3

'''
MOdule for handling user authentication
'''

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models import Token, User