import pdfplumber
import re
import sqlite3
import json

# Keywords to search in product names
keywords = [
    "Noodle", "dumplings", "pasta sauce", "laundry liquid", "lasagne", 
    "sausages", "steak", "lamb", "chicken", "bacon", "apples", 
    "kiwifruit", "celery", "broccoli", "onions", "carrots", "beans"
]

# Array to store the structured results
products = []

# Function to check if a product name contains any keyword
def contains_keyword(product_name):
    product_name_lower = product_name.lower()
    return any(keyword.lower() in product_name_lower for keyword in keywords)

# Function to extract structured data
def parse_product_info(product_line, price_line):
    # Split product and price info by common delimiters
    product_parts = re.split(r'[,|;|\.]', product_line)
    price_parts = re.split(r'[,|;|\.]', price_line)

    # Extract the relevant product details
    for part in product_parts:
        part = part.strip()
        if contains_keyword(part):
            # Create a dictionary for each product
            product_info = {
                "product": part,
                "brand": "Unknown",  # Default brand as 'Unknown' (you can adjust this if brand info is available)
                "price": None,
                "quantity": None
            }

            # Find the corresponding price and quantity from price parts
            for price_part in price_parts:
                # Regex to match prices (e.g., $3.50, $0.78 per 100g, etc.)
                price_match = re.search(r"\$\d+(\.\d{1,2})?", price_part)
                quantity_match = re.search(r"\d+(\.\d+)?(g|kg|ml|L|each|pack|per [\w\s]+)", price_part, re.IGNORECASE)

                if price_match:
                    product_info["price"] = float(price_match.group().replace('$', ''))
                if quantity_match:
                    product_info["quantity"] = quantity_match.group()

            # Add the structured product info to the products list
            products.append(product_info)

# Open the PDF file and extract data
with pdfplumber.open("promotions/COLNSWMETRO_1809_3871966.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            lines = text.split('\n')
            for i in range(len(lines) - 1):
                line = lines[i].strip()
                next_line = lines[i + 1].strip()
                
                if contains_keyword(line):
                    parse_product_info(line, next_line)

# Save the extracted products to a JSON file
json_file = 'products_data.json'
with open(json_file, 'w') as f:
    json.dump(products, f, indent=4)
print(f"Data successfully saved to {json_file}.")

# Database connection
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    product TEXT,
    brand TEXT,
    price REAL,
    quantity TEXT
)
''')

# Insert data into the table
for product in products:
    cursor.execute('''
    INSERT INTO products (product, brand, price, quantity)
    VALUES (?, ?, ?, ?)
    ''', (product['product'], product['brand'], product['price'], product['quantity']))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully inserted into the database.")
