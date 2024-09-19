import re
import pdfplumber
import sqlite3
from datetime import datetime
import os
import json

# Database setup
conn = sqlite3.connect('receipt_data.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS receipts (
                    product_name TEXT,
                    price REAL,
                    quantity TEXT,
                    date TEXT,
                    PRIMARY KEY (product_name, date)
                )''')

# Function to add quantity column if it doesn't exist
def add_quantity_column():
    try:
        cursor.execute("PRAGMA table_info(receipts)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'quantity' not in columns:
            cursor.execute("ALTER TABLE receipts ADD COLUMN quantity TEXT")
            print("Added 'quantity' column to the 'receipts' table.")
        else:
            print("'quantity' column already exists in the 'receipts' table.")
    except sqlite3.OperationalError as e:
        print("Error adding 'quantity' column:", e)

add_quantity_column()

# Function to extract text based on line separation
def extract_text_by_lines(pdf_path):
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text)
    return all_text

# Function to parse the text for product names, prices, quantities, and dates
def parse_receipt_data(texts):
    products = []
    product_name_pattern = r"([A-Za-z\s'\"-]+)(?=\s+\$)"
    product_price_pattern = r"\$([0-9]+\.[0-9]{2})"
    product_quantity_pattern = r"(\d+ml|\d+g|\d+kg|\d+ grams|\d+ kilogram|\d+ eggs)"
    date_patterns = [r'\d{2}/\d{2}/\d{4}', r'\d{4}-\d{2}-\d{2}']

    date_str = None
    for pattern in date_patterns:
        for text in texts:
            date_match = re.search(pattern, text)
            if date_match:
                date_str = date_match.group(0)
                break
        if date_str:
            break
    
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                print(f"Date format error for date string: {date_str}")
                date_obj = None
    else:
        date_obj = None

    for text in texts:
        product_names = re.findall(product_name_pattern, text)
        product_prices = re.findall(product_price_pattern, text)
        product_quantities = re.findall(product_quantity_pattern, text)
        
        min_len = min(len(product_names), len(product_prices), len(product_quantities))
        product_names = product_names[:min_len]
        product_prices = product_prices[:min_len]
        product_quantities = product_quantities[:min_len]

        for name, price, quantity in zip(product_names, product_prices, product_quantities):
            products.append({
                "product_name": name.strip(),
                "price": float(price),
                "quantity": quantity.strip(),
                "date": date_obj.strftime('%Y-%m-%d') if date_obj else None
            })

    return products

# Function to update the database with product data
def update_database(products):
    for product in products:
        product_name = product['product_name']
        price = product['price']
        quantity = product['quantity']
        date_obj = product['date']

        cursor.execute('''
            INSERT OR REPLACE INTO receipts (product_name, price, quantity, date) 
            VALUES (?, ?, ?, ?)
        ''', (product_name, price, quantity, date_obj))
        
        print(f"{product_name:<25} {price:<10.2f} {quantity:<10} {date_obj}")

    conn.commit()

# Function to load Coles data from JSON
def load_coles_data(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    coles_data = {}
    for item in data['productData']:
        key = f"{item['product']} ({item['brand']}) - {item['quantity']}"
        coles_data[key] = item['price']
    return coles_data

# Function to check if PDF prices are lower than Coles prices
def check_prices_against_coles(products, coles_data):
    for product in products:
        product_name = product['product_name']
        pdf_price = product['price']
        pdf_quantity = product['quantity']
        key = f"{product_name} - {pdf_quantity}"
        
        coles_price = coles_data.get(key, None)
        if coles_price is not None:
            if pdf_price < coles_price:
                print(f"Product '{product_name}' is cheaper in the PDF: PDF Price = {pdf_price}, Coles Price = {coles_price}")
            else:
                print(f"Product '{product_name}' is not cheaper in the PDF: PDF Price = {pdf_price}, Coles Price = {coles_price}")
        else:
            print(f"Product '{product_name}' not found in Coles data.")

# Function to process all receipts in a directory
def process_all_receipts(directory_path, coles_data_path):
    coles_data = load_coles_data(coles_data_path)
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing {pdf_path}")
            texts = extract_text_by_lines(pdf_path)
            products = parse_receipt_data(texts)
            update_database(products)
            check_prices_against_coles(products, coles_data)
def print_results():
    cursor.execute('SELECT * FROM receipts')
    rows = cursor.fetchall()
    
    print("\nDatabase Contents:")
    print(f"{'Product Name':<25} {'Price':<10} {'Quantity':<10} {'Date':<15}")
    print("-" * 60)
    
    
# Main function to start processing
def main():
    pdf_path = '/Users/bhakthi/Desktop/Group-7/promotions/COLNSWMETRO_1809_3871966.pdf'  # Path to PDF
    coles_data_path = '/path/to/colesData.json'  # Path to JSON file
    print(f"Processing PDF: {pdf_path}")
    texts = extract_text_by_lines(pdf_path)
    products = parse_receipt_data(texts)
    print_results()
    update_database(products)
    check_prices_against_coles(products, load_coles_data(coles_data_path))

# Example usage
if __name__ == "__main__":
    main()

# Close the connection to the database when done
conn.close()
