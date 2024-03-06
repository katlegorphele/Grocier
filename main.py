from selenium import webdriver
from siteparsers import search_pnp, search_checkers, search_woolworths  

items = {}

def get_grocery_list():
    items = []
    while True:
        item = input("Enter an item for your grocery list (or 'done' to finish): ")
        if item.lower() == 'done':
            break
        items.append(item)
    return items

def main():
    # Get the grocery list from the user
    items = get_grocery_list()

    # Initialize the browser
    browser = webdriver.Firefox()

    # For each item in the grocery list, get the prices from each store
    for item in items:
        pnp_result = search_pnp(browser, item)
        checkers_result = search_checkers(browser, item)
        woolworths_result = search_woolworths(browser, item)

        print(f'Item: {item}')
        print(f'PnP: {pnp_result}')
        print(f'Checkers: {checkers_result}')
        print(f'Woolworths: {woolworths_result}')
        print()
        items[item] = {
            "pnp": pnp_result,
            "checkers": checkers_result,
            "woolworths": woolworths_result
        }

    # Close the browser
    browser.quit()

if __name__ == "__main__":
    main()
