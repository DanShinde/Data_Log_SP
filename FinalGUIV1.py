import asyncio
import multiprocessing
import socket
import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QSizePolicy, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QHeaderView, QLineEdit, QPushButton, QRadioButton, QMessageBox, QSpacerItem, QDateTimeEdit
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor
import sqlite3
from funs import readConfig, configure_logging, processString, timestamping, updateAlarmOutTime, create_table, insert_data_into_table, update_out_time

 
# Set up logger
logger, log_file_path = configure_logging()
create_table()

class MainWindow(QMainWindow):
    
    def __init__(self, control_queue, tcp_process_queue, tcp_process):
        super().__init__()
        self.tcp_process_queue = tcp_process_queue
        self.control_queue = control_queue
        self.control_queue['status'] = 'nothing'
        self.control_queue['para'] =  ('192.168.2.25', 4000, 'connected')
        self.tcp_process = tcp_process
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(100)  # Check for updates every 100ms

        self.setWindowTitle("Alarm Logging Tool")

        # Open the window in maximized form
        self.setWindowState(Qt.WindowMaximized)

        # Create a label for the current date and time
        self.dateTimeLabel = QLabel()
        self.dateTimeLabel.setAlignment(Qt.AlignRight)
        self.dateTimeLabel.setStyleSheet("color: black;")
        self.update_date_time()  # Update the date and time initially

        # Create a label and line edit for the title
        self.titleLabel = QLabel("Alarm Viewer")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet("color: black; background-color: medium aquamarine;")
        self.titleLabel.setFont(QFont("Times New Roman", 20))
        # Create the submit button
        self.submitButton = QPushButton("Submit")
        self.submitButton.clicked.connect(self.update_table)
        self.submitButton.setFixedWidth(100)
        self.submitButton.setStyleSheet("background-color: lightblue;")
        # Create a connect button
        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.connect_function)
        self.connectButton.setFixedWidth(100)
        self.connectButton.setStyleSheet("background-color: lightgreen;")
        self.connectButton.setEnabled(True)
        self.connectButton.clicked.connect(self.start_tcp_client)
        # Create a disconnect button
        self.disconnectButton = QPushButton("Disconnect")
        self.disconnectButton.clicked.connect(self.connect_function)
        self.disconnectButton.setFixedWidth(100)
        self.disconnectButton.setStyleSheet("background-color: lightcoral;")
        self.disconnectButton.setEnabled(False)
        self.disconnectButton.clicked.connect(self.stop_tcp_client)

        # Create an Export button
        self.ExportButton = QPushButton("Export")
        self.ExportButton.clicked.connect(self.export_data)
        self.ExportButton.setFixedWidth(100)
        self.ExportButton.setStyleSheet("background-color: lightsalmon;")
        # Line edit for entering the number of rows

        self.rowCountLabel = QLabel("Selected Rows:")
        self.rowCountLineEdit = QLineEdit()
        self.rowCountLineEdit.setText("0")  # Default value
        self.rowCountLineEdit.setEnabled(False)
        self.rowCountLineEdit.setFixedWidth(50)  # Set fixed width
        self.rowCountLineEdit.setAlignment(Qt.AlignLeft)  # Align text to the right
        self.rowCountLabel.setFixedWidth(80)

        # Start date and end date selection widgets
        self.startDateEdit = QDateTimeEdit()
        self.startDateEdit.setDisplayFormat("yyyy-MM-dd")
        self.startDateEdit.setDateTime(QDateTime.currentDateTime())
        self.endDateEdit = QDateTimeEdit()
        self.endDateEdit.setDisplayFormat("yyyy-MM-dd")
        self.endDateEdit.setDateTime(QDateTime.currentDateTime())

        # Text fields for IP port and connection key
        host, port, connkey = readConfig()
        self.IPLineEdit = QLineEdit()
        self.IPLineEdit.setPlaceholderText("Enter IP")
        self.IPLineEdit.setText(host)
        self.PortLineEdit = QLineEdit()
        self.PortLineEdit.setPlaceholderText("Enter Port No")
        self.PortLineEdit.setText(str(port))
        self.connectionKeyLineEdit = QLineEdit()
        self.connectionKeyLineEdit.setPlaceholderText("Enter Connection Key")
        self.connectionKeyLineEdit.setText(connkey)

        
        

        # Create a QHBoxLayout to hold the rowCountLabel, rowCountLineEdit, and submitButton
        row_count_layout = QHBoxLayout()
        row_count_layout.addWidget(self.rowCountLabel)
        row_count_layout.addWidget(self.rowCountLineEdit)
        row_count_layout.addWidget(self.submitButton)
        row_count_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))  # Add spacer item
        row_count_layout.addWidget(self.IPLineEdit)
        row_count_layout.addWidget(self.PortLineEdit)
        row_count_layout.addWidget(self.connectionKeyLineEdit)
        row_count_layout.addWidget(self.connectButton)
        row_count_layout.addWidget(self.disconnectButton)
        row_count_layout.addWidget(QLabel("Start Date:"))
        row_count_layout.addWidget(self.startDateEdit)
        row_count_layout.addWidget(QLabel("End Date:"))
        row_count_layout.addWidget(self.endDateEdit)
        row_count_layout.addWidget(self.ExportButton)

        row_count_layout.setContentsMargins(0, 0, 0, 0)  # Set contents margins to remove extra space

        # Align widgets to the left side
        row_count_layout.setAlignment(Qt.AlignLeft)

        # Radio button group for user choice
        self.radioGroup = QRadioButton("View Complete Table")
        self.radioGroup.setChecked(True)
        self.radioGroup.toggled.connect(self.radio_button_changed)

        # Create a QTableWidget to display the data
        self.tableWidget = QTableWidget()

        # Create a central widget to hold the title label and the table
        centralWidget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.dateTimeLabel)
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.radioGroup)
        layout.addLayout(row_count_layout)  # Add QHBoxLayout to the main layout
        layout.addWidget(self.tableWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        
   
# Resize the columns to fit the contents
        column_widths = [40, 100, 150, 150, 100, 100,90, 70, 70, 70, 70, 315]  # Example widths for each column
        for i in range(self.tableWidget.columnCount()):
            self.tableWidget.setColumnWidth(i, column_widths[i])

        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


        # Update the date and time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)

        # Apply style sheets to buttons
        self.submitButton.setStyleSheet("background-color: lightblue;")
        self.connectButton.setStyleSheet("background-color: lightgreen;")
        self.disconnectButton.setStyleSheet("background-color: lightcoral;")
        self.ExportButton.setStyleSheet("background-color: lightsalmon;")
        self.update_table()
        self.show()

    def start_tcp_client(self):
        ip = self.IPLineEdit.text()
        port = int(self.PortLineEdit.text())
        connkey = self.connectionKeyLineEdit.text()
        self.control_queue['status'] = 'start'
        self.control_queue['para'] =  (ip, port, connkey)
        print(self.control_queue)

        #self.statusLabel.setText('Status: Connected')

    def stop_tcp_client(self):
        # self.control_queue.put('stop')
        self.control_queue['status'] = 'stop'
        print(self.control_queue)
        print('Stop Command sent')
        #self.statusLabel.setText('Status: Disconnected')

    def check_for_updates(self):
        if self.tcp_process_queue.empty():
            return
        data = self.tcp_process_queue.get()
        print(data)
        if data == 'Status: Connected':
            self.connectButton.setEnabled(False)
            self.disconnectButton.setEnabled(True)
        if data == 'Status: Disconnected':
            self.connectButton.setEnabled(True)
            self.disconnectButton.setEnabled(False)
        if data == 'update_table':
            self.update_table()
            print('table_updatedout')

            # print('tcp status received :', data)
            # Update the GUI based on the received data
            # self.statusLabel.setText(f"Received: {data}")

    def closeEvent(self, event):
        # self.control_queue.put(('stop',))
        self.control_queue['status'] = 'stop'
        self.tcp_process.terminate()
        self.tcp_process.join()
        event.accept()

    def update_date_time(self):
        # Get the current date and time
        currentDateTime = QDateTime.currentDateTime()
        # Format the date and time
        formattedDateTime = currentDateTime.toString(Qt.DefaultLocaleLongDate)
        # Update the label text
        self.dateTimeLabel.setText(formattedDateTime)
        self.dateTimeLabel.setFont(QFont("Times New Roman", 12, QFont.Bold))

    def radio_button_changed(self):
        # Enable or disable the line edit based on the radio button selection
        self.rowCountLineEdit.setEnabled(not self.radioGroup.isChecked())

    def update_table(self):
        # Clear existing table data
        self.tableWidget.clear()

        if self.radioGroup.isChecked():
            # Select complete table
            selected_rows = self.select_all_entries()
        else:
            # Select the last n entries from the database
            n = int(self.rowCountLineEdit.text())
            if n <= 0:
                QMessageBox.warning(self, "Warning", "Please enter a value greater than zero for the number of rows.")
                return
            selected_rows = self.select_last_n_entries(n)

        # Display the selected rows in the table
        self.display_selected_rows(selected_rows)

    def select_all_entries(self):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('DataLogger.db')
            cur = conn.cursor()

            # Execute the query to select all entries
            cur.execute("""SELECT InTimestamp,
                        OutTimestamp ,
                        Duration ,
                        Category ,
                        SubCategory ,
                        GroupNo ,
                        ZoneNo ,
                        ModuleNo ,
                        AlarmState ,
                 
                        Alarm FROM AlarmTable""")
            # Fetch all the selected rows
            rows = cur.fetchall()

            # Return the selected rows
            # print(rows)
            return rows

        except sqlite3.Error as e:
            print("Error selecting entries:", e)
            return []

        finally:
            # Close the connection
            conn.close()

    def select_last_n_entries(self, n):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('DataLogger.db')
            cur = conn.cursor()

            # Execute the query to select the last n entries
            cur.execute("""SELECT InTimestamp,
                        OutTimestamp ,
                        Duration ,
                        Category ,
                        SubCategory ,
                        GroupNo ,
                        ZoneNo ,
                        ModuleNo ,
                        AlarmState ,
                        Alarm FROM AlarmTable""")
            # Fetch all the selected rows
            rows = cur.fetchall()

            # Return the selected rows
            return rows

        except sqlite3.Error as e:
            print("Error selecting entries:", e)
            return []

        finally:
            # Close the connection
            conn.close()

    def display_selected_rows(self, rows):
        # Set the number of rows and columns in the table
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(rows[0]))

        # Set the table headers
        headers = ['InTimestamp','OutTimestamp','Duration', 'Category','SubCategory','GroupNo','ZoneNo','ModuleNo','AlarmState','Alarm Description']  # Replace with actual column names
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Insert data into the table
        for i, row in enumerate(rows):
            print(type(row))
            if row[3] == 'Error':
                color = QColor(255,100,100)
            if row[3] == 'Status':
                color = QColor(125,125,125)

            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setBackground(color)

                self.tableWidget.setItem(i, j, item)
                # print(i,j,value)
                # Align text in columns 1, 7, 8, and 9 to the center
                # if j in [0, 4, 7, 8, 9, 10]:
                item.setTextAlignment(Qt.AlignCenter)

        # Resize the columns to fit the contents


        # Set header style
        header = self.tableWidget.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setStyleSheet("QHeaderView::section { background-color: MediumOrchid1; color: white; }")  # Change background color to blue and text color to yellow
        header.setFont(QFont("Times New Roman", 10, QFont.Normal))
        
        # Resize the columns to fit the contents
        column_widths = [40, 100, 150, 150, 100, 100,90, 70, 70, 70, 70, 315]  # Example widths for each column
        # for i in range(self.tableWidget.columnCount()):
        #     self.tableWidget.setColumnWidth(i, column_widths[i])
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resetHorizontalScrollMode()

    def connect_function(self):
        # Implement your connect function here
        pass

    def export_data(self):
        start_date = self.startDateEdit.dateTime().toString("yyyy-MM-dd")
        end_date = self.endDateEdit.dateTime().toString("yyyy-MM-dd")
        ip_port = self.IPLineEdit.text()
        connection_key = self.connectionKeyLineEdit.text()
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('DataLogger.db')
            cur = conn.cursor()

            # Execute the query to select rows within the specified date range
            cur.execute("SELECT * FROM AlarmTable WHERE InTimestamp BETWEEN ? AND ?", (start_date, end_date))

            # Fetch all the selected rows
            rows = cur.fetchall()

            # Export the data
            with open('exported_data.csv', 'w') as f:
                # Write headers
                headers = ['InTimestamp','OutTimestamp','Duration', 'Category','SubCategory','GroupNo','ZoneNo','ModuleNo','Alarm','AlarmState']
                f.write(','.join(headers) + '\n')

                # Write rows
                for row in rows:
                    f.write(','.join(map(str, row)) + '\n')

            QMessageBox.information(self, "Export", "Data exported successfully!")

        except sqlite3.Error as e:
            print("Error exporting data:", e)

        finally:
            # Close the connection
            conn.close()

# async def receive_data(client_socket):
#     loop = asyncio.get_event_loop()
#     data = await loop.sock_recv(client_socket, 1024)
#     return data.decode()

def receive_data(client_socket, PendingAlarms, tcp_process_queue):
    while True:
        try:
            received = client_socket.recv(1024).decode()
            toListID = received[:12] + received[42:-2]
            tcp_process_queue.put('update_table')
            if not received:
                break  # No more data, exit inner loop
            if toListID in PendingAlarms:
                outTime, state = timestamping(received)
                updateAlarmOutTime(log_file_path, toListID, 3, outTime)
                update_out_time(','.join((outTime,state,toListID)))
                # print('Updated time')
                PendingAlarms.remove(toListID)
            else:
                PendingAlarms.append(toListID)
                try:
                    alarm_status, toLog, itime = processString(received)
                    # print('Adding Alarm')
                    if alarm_status == 'P':
                        ilog = ','.join([itime, '', toLog, toListID])
                    else:
                        ilog = ','.join(['', itime, toLog, toListID])
                    logger.info(ilog)
                    insert_data_into_table(ilog + ','+ alarm_status)
                except:
                    pass
        except (socket.error, ConnectionResetError) as e:
            # tcp_process_queue.put('Status: Disconnected')
            if client_socket:
                client_socket.close()
            running = False
            break


def tcp_client(tcp_process_queue, control_queue):
    global logger
    client_socket = None
    running = False
    PendingAlarms = []

    # print('CLietProcess')

    while True:
        # print('start received')
        # print(control_queue)
        try:
            if control_queue['status'] != 'nothing':
                command = control_queue['para']
                action  = control_queue['status']
                # print(command)
                print('socket is running :', running)
                if action == 'start' and not running:
                    ip, port, connkey = command
                    # print('start received')
                    try:
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client_socket.connect((ip, port))
                        client_socket.send(connkey.encode())
                        running = True
                        tcp_process_queue.put('Status: Connected')
                        control_queue['status'] = 'nothing'
                        receive_thread = threading.Thread(target=receive_data, args=(client_socket, PendingAlarms, tcp_process_queue))
                        receive_thread.start()

                    except (socket.error, socket.timeout) as e:
                        tcp_process_queue.put(f'Status: Connection failed: {e}')
                        if client_socket:
                            client_socket.close()
                        running = False
                        control_queue['status'] = 'nothing'
                        receive_thread.stop()

                elif action =='stop' and running:
                    if client_socket:
                        client_socket.close()
                    running = False
                    tcp_process_queue.put('Status: Disconnected')
                    control_queue['status'] = 'nothing'

                else:
                    print('Wrong command received', command)

            # if running and client_socket:
                # try:
                #     # Example: sending a ping message
                #     # client_socket.sendall(b'ping')
                #     #  while True:
                    

                #     received = client_socket.recv(1024).decode()
                #     toListID = received[:12] +  received[42:-2]


                #     if toListID in PendingAlarms:
                #         outTime = timestamping(received)
                #         updateAlarmOutTime(log_file_path, toListID, 3, outTime)
                #         print('Updated time')
                #         PendingAlarms.remove(toListID)
                #     else:
                #         PendingAlarms.append(toListID)
                #         alarm_status, toLog, itime = processString(received)
                #         print('Adding Alarm')
                #         if alarm_status =='P':
                #             ilog = ','.join([itime,'',toLog, toListID])
                #         else:
                #             ilog = ','.join(['',itime,toLog, toListID])
                #         logger.info(ilog)
                #     PendingAlarms.append

                #     action  = control_queue['status']
                #     if action =='stop' and running:
                #         if client_socket:
                #             client_socket.close()
                #         running = False
                #         tcp_process_queue.put('Status: Disconnected')
                #         control_queue['status'] = 'nothing'

                # except (socket.error, ConnectionResetError) as e:
                #     tcp_process_queue.put('Status: Disconnected')
                #     if client_socket:
                #         client_socket.close()
                #     running = False
        except Exception as e :
            print('TCP process exception : ', e)
        # time.sleep(0.1)  # Avoid busy waiting

    if client_socket:
        client_socket.close()
        print('Socket Closed')
# def main():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    manager = multiprocessing.Manager()
    control_queue = manager.dict() #multiprocessing.Queue()
    tcp_process_queue = multiprocessing.Queue()

    tcp_process = multiprocessing.Process(target=tcp_client, args=(tcp_process_queue, control_queue))
    tcp_process.start()

    main_window = MainWindow(control_queue, tcp_process_queue, tcp_process)

    sys.exit(app.exec_())

    tcp_process.terminate()
    tcp_process.join()




    main_window = MainWindow(control_queue)