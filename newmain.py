import argparse
import asyncio
from getpass import getpass
from selenium import webdriver
from userreg import User, login_user, register_user
from siteparsers import search_pnp, search_checkers, search_woolworths

BASE_URL = "http://localhost:8000"


def register(username, password):
    response = asyncio.run(register_user(User(username=username, password=password)))
    return response


async def login():
    print("Logging in...")
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    # Call the FastAPI login function
    response_model = await login_user(User(username=username, password=password))

    if response_model:
        return response_model["access_token"]
    else:
        return ""


def get_grocery_list():
    items = []
    while True:
        item = input("Enter an item for your grocery list (or 'done' to finish): ")
        if item.lower() == 'done':
            break
        items.append(item)
    return items


def fetch_prices(browser, items):
    prices = {}
    for item in items:
        pnp_result = search_pnp(browser, item)
        checkers_result = search_checkers(browser, item)
        woolworths_result = search_woolworths(browser, item)

        prices[item] = {
            "PnP": pnp_result,
            "Checkers": checkers_result,
            "Woolworths": woolworths_result
        }
    return prices


def main():
    parser = argparse.ArgumentParser(description="CLI Interface for FastAPI Shopping List Application")
    parser.add_argument("command", choices=["register", "login", "create", "list", "update", "delete", "prices"],
                        help="Command to execute")
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
            browser = webdriver.Firefox()
            prices = fetch_prices(browser, items)
            print(prices)
            browser.quit()
        else:
            print("Login failed. Cannot create shopping list.")
    # Add other commands as needed


if __name__ == "__main__":
    main()
