import sqlite3

# Connect to the database
conn = sqlite3.connect('./health_data.db')
cursor = conn.cursor()

# Get table info
cursor.execute('PRAGMA table_info(uploads)')
columns = cursor.fetchall()
print('\nUploads table columns:')
print([col[1] for col in columns])

# Get all uploads
cursor.execute('SELECT * FROM uploads')
rows = cursor.fetchall()
print('\nUploads data:')
if not rows:
    print('No uploads found in the database')
else:
    for row in rows:
        print(row)

# Close connection
conn.close()