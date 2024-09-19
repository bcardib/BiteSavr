import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('path_to_your_database.db')
cursor = conn.cursor()

# Execute SQL commands
cursor.execute('PRAGMA table_info(receipts);')
table_info = cursor.fetchall()
print(table_info)

# Example of creating a new table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS new_receipts (
        store TEXT,
        product TEXT,
        brand TEXT,
        price REAL,
        quantity TEXT
    )
''')
conn.commit()

# Example of renaming a table
cursor.execute('ALTER TABLE new_receipts RENAME TO receipts;')
conn.commit()

# Close the connection
conn.close()
