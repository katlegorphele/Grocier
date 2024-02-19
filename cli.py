# cli.py

import argparse
import asyncio
from getpass import getpass
from userreg import register_user, login_user, create_shopping_list, get_shopping_lists, update_shopping_list, delete_shopping_list, Token, User

async def register():
    print("Registering a new user...")
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    # Create a User object to match the expected input of the FastAPI register function
    user = User(username=username, password=password)
    
    # Call the FastAPI register function
    response_model = await register_user(user)
    
    if response_model:
        print("User registered successfully.")
    else:
        print("Registration failed.")

def login():
    print("Logging in...")
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    # Create a User object to match the expected input of the FastAPI login function
    user = {"username": username, "password": password}
    
    # Call the FastAPI login function
    response_model = login_user(user)
    
    if response_model:
        print("Login successful.")
        # Extract access_token from the response model
        access_token = response_model["access_token"]
        return access_token
    else:
        print("Login failed.")

def main():
    parser = argparse.ArgumentParser(description="CLI Program for User Authentication and Shopping List Management")
    parser.add_argument("--register", action="store_true", help="Register a new user")
    args = parser.parse_args()

    if args.register:
        register()
    else:
        access_token = login()
        if access_token:
            # Add logic for managing shopping lists here
            pass

if __name__ == "__main__":
    main()
