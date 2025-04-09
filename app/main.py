from flask import Flask, render_template, request, redirect, url_for
import concurrent.futures
import json
import os
import requests
from bs4 import BeautifulSoup
#from config import BUYING_SITES
import logging
from pathlib import Path
import sys

# for progress bar
from flask import jsonify
import threading

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

BOOKS_FILE = 'books.json'
CONFIG_FILE = 'config.json'
APP_NAME = 'buchdashboard'

# Global variables to track progress for progress bar
scraping_in_progress = False
scraping_progress = 0
total_books = 0

def get_xdg_config_home():
    """
    Get the XDG configuration home directory.
    Follows the XDG Base Directory Specification.
    """
    # Check if XDG_CONFIG_HOME is set, otherwise use default
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        return Path(xdg_config_home)
    
    # Default to ~/.config if not set
    return Path.home() / '.config'

def get_app_config_dir(APP_NAME):
    """
    Get the configuration directory for a specific application.
    """
    config_home = get_xdg_config_home()
    app_config_dir = config_home / APP_NAME
    
    # Create the directory if it doesn't exist
    app_config_dir.mkdir(parents=True, exist_ok=True)
    
    return app_config_dir

def get_config_value(value):
    config_dir = get_app_config_dir(APP_NAME)
    config_path = config_dir / CONFIG_FILE

    if not os.path.exists(config_path):
        write_default_config(config_dir)
    
    with open(config_path, 'r') as config_file:
        return json.load(config_file)[value]

def write_default_config(config_dir):
    try:
        with open('app/config_default.json','r') as default_config_file:
            default_config = default_config_file.read()
        with open(config_dir / CONFIG_FILE, 'w') as config_file:
            config_file.write(default_config)
    except Exception as e:
        logging.error(e)
        sys.exit(1)

def read_books():
    """Read books from the JSON file."""
    config_dir = get_app_config_dir(APP_NAME)
    books_path = config_dir / BOOKS_FILE
    if os.path.exists(books_path):
        with open(books_path, 'r') as file:
            return json.load(file)
    return []

def write_books(books):
    """Write books to the JSON file."""
    config_dir = get_app_config_dir(APP_NAME)
    books_path = config_dir / BOOKS_FILE
    with open(books_path, 'w') as file:
        json.dump(books, file, indent=4)

def get_next_id():
    """Get the next ID for the new book."""
    books = read_books()
    if books:
        return max(book['id'] for book in books) + 1
    return 1

def scrape_price(url):
    """Scrapes a book price from the given URL."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        price = None
        if 'booklooker' in url:
            price_tag = soup.find('span', {'class': 'price'})
        elif 'zvab' in url or 'abebooks' in url:
            price_tag = soup.find('p', {'id':'item-price-1'})
        elif 'medimops' in url:
            price_tag = soup.find('span', {'data-testid':'product-price-display-desktop'})
        elif 'rebuy' in url:
            price_tag = soup.find('span', {'data-cy':'product-price'})
        elif 'bookbot' in url:
            #pattern = re.compile(r"ProductItemPrice_root__[a-zA-Z0-9]+")
            price_tag = soup.find('span', {'class':"ProductItemPrice_root__vswyO"})
        elif 'eurobuch' in url:
            price_tag = soup.find('span', {'id':'results_min_price'})
        elif 'buchfreund' in url:
            price_tag = soup.find('div', {'class':'product-price'}).find('span', {'class':'text-nowrap'})
        elif 'ebay' in url:
            price_tag = soup.find('span', {'class':'s-item__price'})

        if price_tag:
            price = price_tag.text.strip()

        return price
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def parse_price(price_str):
    """Parse the price string and return a float value."""
    # Remove the non-breaking space character and currency symbol (e.g., EUR, €, etc.)
    price_str = price_str.replace("\u00a0", "").replace("EUR", "").replace("€", "").strip()
    
    try:
        # Convert to float
        return float(price_str.replace(",", "."))
    except ValueError:
        logging.error(f"Error parsing price string '{price_str}'")
        return None

def process_book_prices(book):
    """
    Process prices for a single book concurrently across different sites.
    
    Args:
        book (dict): A dictionary containing book information including ISBN.
    
    Returns:
        dict: Updated book dictionary with sorted prices.
    """
    book_prices = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create futures for price scraping on different sites for this book
        futures = {
            executor.submit(scrape_price, url_template.format(isbn=book['isbn'])): site
            for site, url_template in get_config_value('BUYING_SITES').items()
        }
        
        # Process the results as they complete
        for future in concurrent.futures.as_completed(futures):
            site = futures[future]
            try:
                price = future.result()
                if price:
                    book_prices[site] = price
            except Exception as e:
                logging.error(f"Error scraping price for book {book.get('title', 'Unknown')} on site {site}: {e}")
    
    # Sort prices
    sorted_prices = []
    for site, price in book_prices.items():
        try:
            # Remove the currency symbol (assume it's the first character)
            price_value = parse_price(price)
            sorted_prices.append((site, price_value))
        except ValueError as e:
            logging.error(f"Error converting price '{price}' for site '{site}' to float: {e}")
    
    # Sort by price value (ascending order)
    sorted_prices.sort(key=lambda x: x[1])
    sorted_prices_dict = {site: f"{price:.2f}€" for site, price in sorted_prices}

    # Set under_limit to true if under limit
    book["under_limit"] = False
    price_limit = book.get('price_limit', 0)
    if price_limit > 0:
        for price in sorted_prices_dict.items():
            if parse_price(price[1]) <= price_limit:
                book["under_limit"] = True
                break
    
    # Update book with sorted prices
    book['prices'] = sorted_prices_dict
    return book

def scrape_all_prices():
    """
    Scrapes prices for all books concurrently and writes updated books.
    """
    global scraping_in_progress, scraping_progress, total_books
    
    books = read_books()
    total_books = len(books)
    scraping_progress = 0
    scraping_in_progress = True
    
    # Process books concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit processing for each book
        futures = {executor.submit(process_book_prices, book): book for book in books}
        
        # Collect results
        updated_books = []
        for future in concurrent.futures.as_completed(futures):
            try:
                updated_book = future.result()
                updated_books.append(updated_book)
                scraping_progress += 1
            except Exception as e:
                logging.error(f"Error processing book: {e}")
                scraping_progress += 1
        
        # Ensure we maintain the original order if needed
        updated_books.sort(key=lambda b: books.index(b))
    
    # Write updated books
    write_books(updated_books)
    scraping_in_progress = False

@app.route('/')
def index():
    books = read_books()
    return render_template('index.html', books=books, BUYING_SITES=get_config_value('BUYING_SITES'))

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        links = request.form.get('links', '').split(',')
        book = {
            'id': get_next_id(),
            'title': title,
            'isbn': isbn,
            'links': [link.strip() for link in links if link.strip()],
            'prices': {},  # Initialize with empty prices
            'price_limit': float(request.form.get('price_limit') or 0)  # 0 means no limit
        }
        books = read_books()
        books.append(book)
        write_books(books)
        return redirect(url_for('index'))
    return render_template('book_edit.html')

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    books = read_books()
    book = next((book for book in books if book['id'] == book_id), None)
    if not book:
        return redirect(url_for('index'))

    if request.method == 'POST':
        book['title'] = request.form['title']
        book['isbn'] = request.form['isbn']
        book['links'] = request.form.get('links', '').split(',')
        book['price_limit'] = float(request.form.get('price_limit') or 0)
        write_books(books)
        return redirect(url_for('index'))

    return render_template('book_edit.html', book=book)

@app.route('/scrape_prices/<int:book_id>')
def scrape_prices(book_id):
    books = read_books()
    book = next((book for book in books if book['id'] == book_id), None)
    if not book:
        return redirect(url_for('index'))

    book = process_book_prices(book)
    write_books(books)

    return redirect(url_for('index'))

@app.route('/scrape_all_prices', methods=['POST'])
def scrape_all_prices_route():
    """Trigger scraping all books' prices."""
    threading.Thread(target=scrape_all_prices).start()
    return redirect(url_for('index'))

@app.route('/scraping_status')
def scraping_status():
    """Return the current scraping progress."""
    return jsonify({
        'in_progress': scraping_in_progress,
        'progress': scraping_progress,
        'total': total_books,
        'percentage': int((scraping_progress / total_books * 100) if total_books > 0 else 0)
    })

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    books = read_books()
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        books.remove(book)  # Remove the book from the list
        write_books(books)  # Update the JSON file
    return redirect(url_for('index'))

def main():
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)
#    app.run(debug=True)
    
if __name__ == '__main__':
    main()

