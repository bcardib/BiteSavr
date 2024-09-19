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
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    print("Extracted Text:", text)  
    return text

# Function to parse the text for product names, prices, brands, and quantities
def parse_receipt_data(text):
    products = []
    # Regex to match product names and prices (adjust as needed for receipt format)
    product_pattern = r'([a-zA-Z\s]+)\s+(\d+\.\d{2})'
    date_pattern = r'\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}'  # Adjust as necessary
    
    # Find the date
    date_match = re.search(date_pattern, text)
    if date_match:
        date_str = date_match.group(0)
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()  
        except ValueError:
            print(f"Date format error for date string: {date_str}")
            date_obj = None
    else:
        date_obj = None
    
    # Find product name and price
    for match in re.finditer(product_pattern, text):
        product_name = match.group(1).strip()
        price = float(match.group(2))
        products.append((product_name, price, date_obj))

    return products


# Function to update the database with product data
def update_database(products):
    for product_name, price, date_obj in products:
        # Check if the product exists in the database
        cursor.execute("SELECT * FROM receipts WHERE product_name=? AND date=?", (product_name, date_obj))
        existing_entry = cursor.fetchone()

        if existing_entry:
            # Update entry if the new date is later
            cursor.execute('''UPDATE receipts SET price=?, date=? WHERE product_name=? AND date=?''', 
                           (price, date_obj.strftime('%Y-%m-%d'), product_name, date_obj.strftime('%Y-%m-%d')))
            print(f"Updated {product_name} with new price {price} and date {date_obj}")
        else:
            # Insert new entry
            cursor.execute('''INSERT INTO receipts (product_name, price, date) 
                              VALUES (?, ?, ?)''', 
                           (product_name, price, date_obj.strftime('%Y-%m-%d')))
            print(f"Inserted {product_name} with price {price} and date {date_obj}")
    
    conn.commit()

# Function to print all results from the database
def print_results():
    cursor.execute('SELECT * FROM receipts')
    rows = cursor.fetchall()
    
    print("\nDatabase Contents:")
    print(f"{'Product Name':<20} {'Price':<10} {'Date':<15}")
    print("-" * 45)
    for row in rows:
        product_name, price, date = row
        print(f"{product_name:<20} {price:<10} {date:<15}")
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
    pdf_path = '/Users/bhakthi/Desktop/Group-7/promotions/COLNSWMETRO_1809_3871966.pdf'  # Path to PDF
    print(f"Processing PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    products = parse_receipt_data(text)
    update_database(products)
    print_results() # Print the results after processing

# Example usage
if __name__ == "__main__":
    main()

# Close the connection to the database when done
conn.close()
