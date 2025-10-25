#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('health_data.db')
cursor = conn.cursor()

print('🔍 Checking current database contents:')
print('=' * 50)

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'Found {len(tables)} tables:')
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'  {table_name}: {count} records')
    except Exception as e:
        print(f'  {table_name}: Error - {str(e)}')

print('\n📊 Secure computations details:')
try:
    cursor.execute('SELECT id, computation_id, status, created_at FROM secure_computations LIMIT 10')
    computations = cursor.fetchall()
    if computations:
        for comp in computations:
            print(f'  ID: {comp[0]}, Status: {comp[2]}, Created: {comp[3]}')
    else:
        print('  No secure computations found')
except Exception as e:
    print(f'  Error checking computations: {str(e)}')

print('\n📁 Checking uploads:')
try:
    cursor.execute('SELECT COUNT(*) FROM uploads')
    upload_count = cursor.fetchone()[0]
    print(f'  Upload records: {upload_count}')

    if upload_count > 0:
        cursor.execute('SELECT filename, org_id, status FROM uploads LIMIT 5')
        uploads = cursor.fetchall()
        for upload in uploads:
            print(f'    {upload[0]} (org: {upload[1]}, status: {upload[2]})')
except Exception as e:
    print(f'  Error checking uploads: {str(e)}')

conn.close()
print('\n✅ Database check complete')
