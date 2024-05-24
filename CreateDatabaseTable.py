import sqlite3
import os
import datetime

def create_table():
    # Prompt for table name and database name
    table_name = input("Enter table name: ")
    database_name = input("Enter database name: ")

    # Check if the database file already exists
    if not os.path.exists(database_name):
        # Create the database file if it doesn't exist
        open(database_name, 'a').close()
        print("Database created successfully.")
    else:
        print("Database already exists.")

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()

        # Check if the table already exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_exists = cur.fetchone()
        if table_exists:
            print("Table already exists.")
            return

        # Create a table with the specified name and schema
        cur.execute(f'''CREATE TABLE {table_name} (
                        id INTEGER PRIMARY KEY,
                        Info TEXT,
                        InTimestamp TEXT,
                        OutTimestamp TEXT,
                        Duration TEXT,
                        Category TEXT,
                        SubCategory TEXT,
                        GroupNo TEXT,
                        ZoneNo TEXT,
                        ModuleNo TEXT,
                        Alarm TEXT,
                        MsgKey TEXT,
                        AlarmState TEXT
                        
                    )''')
        conn.commit()
        print("Table created successfully.")
    except sqlite3.Error as e:
        print("Error creating table:", e)
    finally:
        # Close the connection
        conn.close()

# Call the function to create the table
create_table()
