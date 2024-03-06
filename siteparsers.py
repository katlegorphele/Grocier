from bs4 import BeautifulSoup


def search_pnp(browser, item):
    # check to see if item has spaces and replace with %20
    item_url = item.replace(' ', '%20')

    browser.get(f'https://www.pnp.co.za/search/{item_url}')

    # Get the HTML of the page
    html = browser.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    # Find the first product item
    product_item = soup.find('div', class_='product-grid-item list-mobile')

    if product_item is not None:
        product_name = product_item.get('data-cnstrc-item-name')
        product_price = product_item.get('data-cnstrc-item-price')
        return f'Product Name: {product_name}, Product Price: R{product_price}'
    else:
        return 'No results found'


def search_checkers(browser, item):
    item = item.replace(' ', '%20')
    browser.get(f'https://www.checkers.co.za/search/all?q={item}')

    # Get the HTML of the page
    html = browser.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    # Find the first product item
    product_item = soup.find('div', class_="item-product")

    if product_item is not None:
        # Find the product name
        product_name_tag = product_item.find('h3', class_='item-product__name').find('a')
        product_name = product_name_tag.get('title') if product_name_tag else 'No product name found'

        # Find the product price
        product_price_tag = product_item.find('span', class_='now')
        product_price = product_price_tag.text if product_price_tag else 'No product price found'

        return f'Product Name: {product_name}, Product Price: {product_price}'
    else:
        return 'No results found'


def search_woolworths(browser, item):
    item = item.replace(' ', '%20')
    # Code to search Woolworths, parse the HTML, and return the product name and price
    browser.get(f'https://www.woolworths.co.za/cat?Ntt={item}&Dy=1')

    # Get the page html
    html = browser.page_source
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')    

    # Find the first product item
    product_item = soup.find('div', class_="product-list__item")

    if product_item is not None:
        # Find the product name
        product_name_tag = product_item.find('div', class_='range--title product-card__name').find('a')
        product_name = product_name_tag.text.strip() if product_name_tag else 'No product name found'

        # Find the product price
        product_price_tag = product_item.find('strong', class_='price')
        product_price = product_price_tag.text.strip() if product_price_tag else 'No product price found'

        return f'Product Name: {product_name}, Product Price: {product_price}'
    else:
        return 'No results found'

