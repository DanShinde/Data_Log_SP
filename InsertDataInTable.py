import sqlite3
import datetime

def insert_data_into_table():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('DataLogger.db')
        cur = conn.cursor()
        t = datetime.datetime.now()
        t1 = 'A'

        # Get user input for the data row as a single string separated by commas
        data_input = input("Enter values for data_to_insert separated by commas: ")

        # Split the input string by commas and create a list
        data_values = data_input.split(',')

        # Convert datetime strings to datetime objects
        data_values[2] = datetime.datetime.strptime(data_values[2], '%Y-%m-%d %H:%M:%S')
        # data_values[3] = datetime.datetime.strptime(data_values[3], '%Y-%m-%d %H:%M:%S')

        # Insert data into the table
        cur.execute('''INSERT INTO DataLogger 
                       (Info,  InTimestamp, OutTimestamp, Duration, Category, SubCategory, 
                        GroupNo, ZoneNo, ModuleNo, Alarm, MsgKey, AlarmState) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data_values[1:])

        # Commit the transaction
        conn.commit()

        print("Values Inserted successfully.")

    except sqlite3.Error as e:
        print("Error inserting values:", e)

    finally:
        # Close the connection
        conn.close()

# Call the function to insert data into the table
insert_data_into_table()
#None,Sample Info,2024-05-22 14:30:00,,,Sample Category,Sample SubCategory,1,2,3,Sample Alarm,EUCN020004EmgStopPressed,