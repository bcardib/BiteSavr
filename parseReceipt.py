import re
import json
import pdfplumber
import sqlite3
from datetime import datetime
import os

# Database setup
conn = sqlite3.connect('receipt_data.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS receipts (
                    product_name TEXT,
                    brand TEXT,
                    price REAL,
                    quantity TEXT,
                    date TEXT,
                    PRIMARY KEY (product_name, brand)
                )''')

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to parse the text for product names, prices, brands, and quantities
def parse_receipt_data(text):
    product_pattern = r'([a-zA-Z\s]+)\s+([a-zA-Z\s]+)\s+\$([0-9]+\.[0-9]{2})\s+(\d+.*)'
    
    products = []
    for match in re.finditer(product_pattern, text):
        product_name = match.group(1).strip()
        brand = match.group(2).strip()
        price = float(match.group(3))
        quantity = match.group(4).strip()

        products.append({
            "store": "Coles",  
            "product": product_name,
            "brand": brand,
            "price": price,
            "quantity": quantity
        })
    
    return products

# Function to update the database with product data
def update_database(products):
    for product in products:
        product_name = product["product"]
        brand = product["brand"]
        price = product["price"]
        quantity = product["quantity"]
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Check if the product already exists in the database
        cursor.execute("SELECT * FROM receipts WHERE product_name=? AND brand=?", (product_name, brand))
        existing_entry = cursor.fetchone()

        if existing_entry:
            print(f"{product_name} ({brand}) already exists in the database.")
        else:
            cursor.execute('''INSERT INTO receipts (product_name, brand, price, quantity, date) 
                              VALUES (?, ?, ?, ?, ?)''', 
                           (product_name, brand, price, quantity, current_date))
            print(f"Inserted {product_name} ({brand}) with price {price} and quantity {quantity}")
    
    conn.commit()

# Function to print all results from the database
def print_results():
    cursor.execute('SELECT * FROM receipts')
    rows = cursor.fetchall()
    
    print("\nDatabase Contents:")
    print(f"{'Product Name':<20} {'Brand':<15} {'Price':<10} {'Quantity':<10} {'Date':<15}")
    print("-" * 70)
    for row in rows:
        product_name, brand, price, quantity, date = row
        print(f"{product_name:<20} {brand:<15} {price:<10} {quantity:<10} {date:<15}")
    print()

# Function to process all receipts in a directory
def process_all_receipts(directory_path):
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.pdf')):
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing {pdf_path}")
            text = extract_text_from_pdf(pdf_path)
            products = parse_receipt_data(text)
            update_database(products)

# Function to process all promotions in a directory (similar to receipts)
def process_all_promotions(directory_path):
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.pdf')):
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing promotion: {pdf_path}")
            text = extract_text_from_pdf(pdf_path)
            products = parse_receipt_data(text)
            update_database(products)

# Main function to start processing
def main():
    receipts_directory = '/Users/bhakthi/Desktop/Group-7/receipts'  
    process_all_receipts(receipts_directory)
    
    # You can add a promotions directory here if needed
    promotions_directory = '/Users/bhakthi/Desktop/Group-7/promotions'  
    process_all_promotions(promotions_directory)

    print_results()  # Print the results after processing

# Example usage
if __name__ == "__main__":
    main()

# Close the connection to the database when done
conn.close()
