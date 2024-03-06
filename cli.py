# cli.py

import argparse
import requests
import asyncio
from getpass import getpass
from userreg import User, login_user

items = {}

def get_grocery_list():
    items = []
    while True:
        item = input("Enter an item for your grocery list (or 'done' to finish): ")
        if item.lower() == 'done':
            break
        items.append(item)
    return items


BASE_URL = "http://localhost:8000"

def register(username, password):
    url = f"{BASE_URL}/register/"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response.json()

async def login() -> str:
    print("Logging in...")
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    # Call the FastAPI login function
    response_model = await login_user(User(username=username, password=password))
    
    if response_model:
        return response_model["access_token"]
    else:
        return ""


def create_shopping_list(token, items:list):
    url = f"{BASE_URL}/shopping_list/create"
    headers = {"Authorization": f"Bearer {token}"}
    data = items
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_shopping_lists(token):
    url = f"{BASE_URL}/shopping_list/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def update_shopping_list(token, shopping_list_id, updated_list):
    url = f"{BASE_URL}/shopping_list/{shopping_list_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(url, json=updated_list, headers=headers)
    return response.json()

def delete_shopping_list(token, shopping_list_id):
    url = f"{BASE_URL}/shopping_list/{shopping_list_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response.json()

def main():
    parser = argparse.ArgumentParser(description="CLI Interface for FastAPI Shopping List Application")
    parser.add_argument("command", choices=["register", "login", "create", "list", "update", "delete"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "register":
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        print(register(username, password))
    elif args.command == "login":
        access_token = asyncio.run(login())
        if access_token:
            print('Login successful')
        else:
            print('Login failed')
    elif args.command == "create":
        access_token = asyncio.run(login())
        if access_token:
            items = get_grocery_list()
            shopping_list = {"items": items}
            print(create_shopping_list(access_token, shopping_list))
        else:
            print("Login failed. Cannot create shopping list.")
    elif args.command == "list":
        token = input("Enter access token: ")
        print(get_shopping_lists(token))
    elif args.command == "update":
        token = input("Enter access token: ")
        shopping_list_id = input("Enter shopping list ID: ")
        updated_list = input("Enter updated shopping list: ")
        print(update_shopping_list(token, shopping_list_id, updated_list))
    elif args.command == "delete":
        token = input("Enter access token: ")
        shopping_list_id = input("Enter shopping list ID: ")
        print(delete_shopping_list(token, shopping_list_id))

if __name__ == "__main__":
    main()
