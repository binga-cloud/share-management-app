import sqlite3
from datetime import datetime

def convert_value(value):
    """Convert database values to proper types"""
    if value is None:
        return None
    elif isinstance(value, (int, float, str)):
        return value
    elif isinstance(value, (bytes, bytearray)):
        return str(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    else:
        return str(value)

print("Starting data transfer...")

# Connect to databases
source = sqlite3.connect('database_backup.db')
dest = sqlite3.connect('database.db')

# Get admin user ID from new database
admin_id = dest.execute("SELECT id FROM user WHERE username='admin'").fetchone()[0]

tables = {
    'user': {'skip': True},  # Skip user table transfer
    'share_purchase': {'extra_cols': [('user_id', admin_id)]},
    'share_sale': {'extra_cols': [('user_id', admin_id)]},
    'dividend': {'extra_cols': [('user_id', admin_id)]},
    'ipo_shares': {'extra_cols': [('user_id', admin_id)]},
    'bonus_shares': {'extra_cols': [('user_id', admin_id)]}
}

# Choose transfer method (uncomment one):
TRANSFER_METHOD = "DELETE_EXISTING"  # Deletes existing data before transfer
# TRANSFER_METHOD = "SKIP_EXISTING"  # Skips records that already exist

for table, config in tables.items():
    print(f"\nTransferring {table} table...")
    
    if config.get('skip'):
        print("Skipping (already exists in new database)")
        continue
        
    try:
        # Get source data
        cursor = source.cursor()
        cursor.execute(f'SELECT * FROM {table}')
        data = cursor.fetchall()
        
        if not data:
            print(f"No data found in {table}, skipping")
            continue
            
        # Get column info
        cursor.execute(f'PRAGMA table_info({table})')
        old_cols = [desc[1] for desc in cursor.fetchall()]
        print(f"Original columns: {', '.join(old_cols)}")
        
        # Prepare for new database structure
        new_cols = old_cols + [col for col, _ in config['extra_cols']]
        placeholders = ', '.join(['?'] * len(new_cols))
        
        # Convert and extend data
        converted_data = []
        for row in data:
            new_row = [convert_value(value) for value in row]
            new_row.extend([val for _, val in config['extra_cols']])
            converted_data.append(new_row)
        
        # Handle existing data based on transfer method
        if TRANSFER_METHOD == "DELETE_EXISTING":
            dest.execute(f'DELETE FROM {table}')
            print("Deleted existing data before transfer")
        
        # Prepare the INSERT statement based on method
        if TRANSFER_METHOD == "SKIP_EXISTING":
            insert_stmt = f'INSERT OR IGNORE INTO {table} ({",".join(new_cols)}) VALUES ({placeholders})'
        else:
            insert_stmt = f'INSERT INTO {table} ({",".join(new_cols)}) VALUES ({placeholders})'
        
        # Insert data
        dest.executemany(insert_stmt, converted_data)
        print(f"Successfully transferred {len(converted_data)} records")
        
    except Exception as e:
        print(f"Error transferring {table}: {str(e)}")
        import traceback
        traceback.print_exc()

# Finalize
dest.commit()
source.close()
dest.close()

print("\nData transfer complete!")
input("Press Enter to exit...")