import sqlite3

def connect_db(db_name='my_database.db'):
    """Connect to the SQLite database (or create it if it doesn't exist)."""
    return sqlite3.connect(db_name)

def create_table():
    """Create the receipts table if it doesn't already exist."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                product_name TEXT PRIMARY KEY,
                price REAL,
                date TEXT
            )
        ''')
        conn.commit()

def insert_or_replace_receipt(product_name, price, date):
    """Insert or replace a receipt record."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO receipts (product_name, price, date) 
            VALUES (?, ?, ?)
        ''', (product_name, price, date))
        conn.commit()

def update_receipt(product_name, price, date):
    """Update a receipt record."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE receipts 
            SET price = ?, date = ?
            WHERE product_name = ?
        ''', (price, date, product_name))
        conn.commit()

def delete_receipt(product_name):
    """Delete a receipt record."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM receipts WHERE product_name = ?
        ''', (product_name,))
        conn.commit()

def query_receipts():
    """Query all receipts and return results."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM receipts')
        return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    create_table()  # Ensure table is created
    
    # Insert or replace a record
    insert_or_replace_receipt("Milk", 2.99, "2024-09-18")
    
    # Update a record
    update_receipt("Milk", 3.49, "2024-09-19")
    
    # Query and print all receipts
    receipts = query_receipts()
    for receipt in receipts:
        print(receipt)
    
    # Delete a record
    delete_receipt("Milk")

    print('deleted hopefully')
     # Query and print all receipts
    receipts = query_receipts()
    print(receipts.__sizeof__)
    for receipt in receipts:
        print(receipt)

    # Insert or replace a record
    insert_or_replace_receipt("Bread", 2.99, "2024-09-18")
    print('added hopefully')
     # Query and print all receipts
    receipts = query_receipts()
    for receipt in receipts:
        print(receipt)
    
