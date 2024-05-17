from datetime import datetime
import logging
import os
import socket
import csv
import json
from time import sleep


def processString(instring):
    categroy = instring[2]
    sub_category = instring[3]
    group_no = instring[4] + instring[5]
    zone_no = instring[6] + instring[7]
    module_no = instring[8:12]
    alaram_status = instring[12]
    ddatetime=instring[13:36]
   
    msg = instring[42:-2]
    if categroy == 'E':
        categroy = 'Error'
    elif categroy =='S':
        categroy = 'Status'
    if sub_category == 'U':
        sub_category = 'User Generated'
    elif sub_category ==  'S':
        sub_category = 'System generatd'  
    if group_no == 'CN':
        group_no = 'Conveyor'
    elif group_no == 'HD':
         group_no = 'HDPS'
    elif group_no == 'VR':
          group_no = 'VRC'

   
    toLog =', '.join([categroy, sub_category, group_no, zone_no, module_no,  msg])
    print(toLog)
    return(alaram_status ,toLog, ddatetime)

def timestamping(instring):
    Dtime = instring[13:36]
    return Dtime



def updateAlarmOutTime(filename, search_string, column_to_update, new_value):
    # Open the CSV file in read mode
    
    
    with open(filename, 'r', newline='') as file:
        # Create a CSV reader object
        reader = csv.reader(file)
        # Create a list to hold the updated rows
        updated_rows = []
        
        # Iterate through each row in the CSV file
        for row in reader:
            # Check if the search string is in the current row
            if search_string in row:
                # Update the value in the specified column
                row[column_to_update] = new_value
            # Add the updated row to the list
            updated_rows.append(row)
    
    # Open the CSV file in write mode
    with open(filename, 'w', newline='') as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the updated rows to the CSV file
        writer.writerows(updated_rows)


def is_first_row_populated(filename):
    # Open the CSV file in read mode
    with open(filename, 'r', newline='') as file:
        # Create a CSV reader object
        reader = csv.reader(file)
        
        # Read the first row
        first_row = next(reader, None)
        
        # Check if the first row is populated
        if first_row:
            # If the first row is not empty, return True
            return True
        else:
            # If the first row is empty, return False
            return False
        


def readConfig():
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        host =  config_data["serverIP"]
        port = int(config_data["Port"])
        connectionKey = config_data["connectionkey"]
        return host, port, connectionKey
    except: 
        config_data = {
                    "serverIP": "192.168.0.1",
                    "Port": 2001,
                    "connectionkey": "Connected"
                }
        json_object = json.dumps(dict, indent=4)

        with open("config.json", "w") as outfile:
            outfile.write(json_object)
        host =  config_data["serverIP"]
        port = int(config_data["Port"])
        connectionKey = config_data["connectionkey"]
        return host, port, connectionKey
        


PendingAlarms = []

def connectListen(host, port, connectionKey):
    global PendingAlarms
    global log_file_path
    global logger
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((host, port)) 
            print('Connected to Host : ', host, ':', port )
            s.send(connectionKey.encode())
            print('Validation Successful')
            while True:
                received = s.recv(1024).decode()
                toListID = received[:12] +  received[42:-2]

                
                if toListID in PendingAlarms:
                    outTime = timestamping(received)
                    updateAlarmOutTime(log_file_path, toListID, 3, outTime)
                    print('Updated time')
                    PendingAlarms.remove(toListID)
                else :
                    PendingAlarms.append(toListID)
                    alarm_status, toLog, itime = processString(received)
                    print('Adding Alarm')
                    if alarm_status =='P':
                        ilog = ','.join([itime,'',toLog, toListID])
                        logger.info(ilog)
                    else :
                        ilog = ','.join(['',itime,toLog, toListID])
                        logger.info(ilog)
                    
                        
                    
                PendingAlarms.append
        except Exception as e:
            s.close()

            
            print(e)
            sleep(3)


def configure_logging():
    # Get the current month and year
    current_month_year = datetime.now().strftime("%Y-%m-%d")
 
    # Create a directory for logs if it doesn't exist
    logs_folder = "Logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
 
    # Define the log file path with the current month and year
    log_file_path = os.path.join(logs_folder, f"TCP_Test_Logger_{current_month_year}.csv")
 
    # Configure logging
    custom_date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s.%(msecs)03d , %(levelname)s , %(message)s' , datefmt=custom_date_format)
    Header = 'In Time, Out time, Category, Sub-Category, Group No, Zone No, Module No, Alarm Error Description,MsgKey'
    if not is_first_row_populated(log_file_path):
        logging.getLogger(__name__).info(Header)
    return logging.getLogger(__name__), log_file_path


