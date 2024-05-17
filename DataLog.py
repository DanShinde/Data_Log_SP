import json
import socket , os
from time import sleep 
import csv,  logging
from datetime import datetime
from ExtraFunctions import *

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
 
# Set up logger
logger, log_file_path = configure_logging()

with open('config.json', 'r') as file:
    config_data = json.load(file)
    
# host = 'localhost'
# port = 2001
# connectionKey = 'Connected'
host =  config_data["serverIP"]
port = int(config_data["Port"])
connectionKey = config_data["connectionkey"]
def readConfig():
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        host =  config_data["serverIP"]
        port = int(config_data["Port"])
        connectionKey = config_data["connectionkey"]
    except: 
        config_data = {
                    "serverIP": "192.168.0.1",
                    "Port": 2001,
                    "connectionkey": "Connected"
                }
        json_object = json.dumps(dict, indent=4)

        with open("config.json", "w") as outfile:
            outfile.write(json_object)


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
            


connectListen(host, port, connectionKey)

