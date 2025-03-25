from flask import Flask
import json

app = Flask(__name__)

@app.route('/books')
def get_books():
    with open(books.json, 'r') as f:
        books = json.parse(f.read())
    return books

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()

