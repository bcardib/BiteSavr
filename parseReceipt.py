import pytesseract
from PIL import Image
import re
import sqlite3
from datetime import datetime
import os

# Database setup
conn = sqlite3.connect('receipt_data.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS receipts (
                    product_name TEXT,
                    price REAL,
                    date TEXT,
                    PRIMARY KEY (product_name)
                )''')

# Function to extract text from image using Tesseract OCR
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Function to parse the text for product names, prices, and dates
def parse_receipt_data(text):
    products = []
    # Regex to match product names and prices (this will depend on receipt format)
    product_pattern = r'([a-zA-Z\s]+)\s+([0-9]+\.[0-9]{2})'
    date_pattern = r'\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}'
    
    # Find the date
    date_match = re.search(date_pattern, text)
    if date_match:
        date_str = date_match.group(0)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d' if '-' in date_str else '%d/%m/%Y').date()
    else:
        date_obj = None
    
    # Find product name and price
    for match in re.finditer(product_pattern, text):
        product_name = match.group(1).strip()
        price = float(match.group(2))
        products.append((product_name, price, date_obj))

    return products

# Function to update the database with receipt data
def update_database(products):
    for product_name, price, date_obj in products:
        # Check if the product exists in the database
        cursor.execute("SELECT * FROM receipts WHERE product_name=?", (product_name,))
        existing_entry = cursor.fetchone()

        if existing_entry:
            # Compare the dates
            existing_date = datetime.strptime(existing_entry[2], '%Y-%m-%d').date()
            if date_obj > existing_date:
                # Update entry if the new date is later
                cursor.execute('''UPDATE receipts SET price=?, date=? WHERE product_name=?''', 
                               (price, date_obj.strftime('%Y-%m-%d'), product_name))
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
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(directory_path, filename)
            print(f"Processing {image_path}")
            text = extract_text_from_image(image_path)
            products = parse_receipt_data(text)
            update_database(products)

# Main function to start processing
def main():
    receipts_directory = 'receipts'  # Directory containing receipt images
    process_all_receipts(receipts_directory)
    print_results()  # Print the results after processing

# Example usage
if __name__ == "__main__":
    main()

# Close the connection to the database
conn.close()
