import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import json
import socket
import os
from time import sleep
import csv
import logging
from datetime import datetime
from ExtraFunctions import *
import asyncio

def configure_logging():
    current_month_year = datetime.now().strftime("%Y-%m-%d")
    logs_folder = "Logs"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    log_file_path = os.path.join(logs_folder, f"TCP_Test_Logger_{current_month_year}.csv")
    custom_date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG, 
                        format='%(asctime)s.%(msecs)03d , %(levelname)s , %(message)s', datefmt=custom_date_format)
    Header = 'In Time, Out time, Category, Sub-Category, Group No, Zone No, Module No, Alarm Error Description,MsgKey'
    if not is_first_row_populated(log_file_path):
        logging.getLogger(__name__).info(Header)
    return logging.getLogger(__name__), log_file_path

logger, log_file_path = configure_logging()

def readConfig():
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        host = config_data["serverIP"]
        port = int(config_data["Port"])
        connectionKey = config_data["connectionkey"]
    except:
        config_data = {
            "serverIP": "192.168.0.1",
            "Port": 2001,
            "connectionkey": "Connected"
        }
        json_object = json.dumps(config_data, indent=4)
        with open("config.json", "w") as outfile:
            outfile.write(json_object)
    return host, port, connectionKey

host, port, connectionKey = readConfig()
PendingAlarms = []

formatui = 'background-color:  #03DAC5; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 20px;  }' #align: center;
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1139, 797)
        MainWindow.setMaximumSize(QtCore.QSize(1187, 797))
        MainWindow.setStyleSheet("QMainWindow{ background:#1E3156; background-color:#1E3156;}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("background:#1E3156;")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 1121, 761))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setStyleSheet("background-color: #BB86FC; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 20px; min-width: 10em; padding: 6px; text-align:center;")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(30, 28))
        self.label_2.setStyleSheet("QLabel{ "+ formatui)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setStyleSheet("QLineEdit{" + formatui)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setText(host)
        self.horizontalLayout.addWidget(self.lineEdit)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(30, 28))
        self.label_3.setStyleSheet("QLabel{ " + formatui)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setMinimumSize(QtCore.QSize(50, 0))
        self.lineEdit_2.setBaseSize(QtCore.QSize(50, 0))
        self.lineEdit_2.setStyleSheet("QLineEdit{ " + formatui)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setText(str(port))
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.BtnConnect = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.BtnConnect.setFont(font)
        self.BtnConnect.setAutoFillBackground(False)
        self.BtnConnect.setStyleSheet("QPushButton{ " + formatui)
        self.BtnConnect.setDefault(False)
        self.BtnConnect.setEnabled(True)
        self.BtnConnect.setObjectName("BtnConnect")
        self.horizontalLayout.addWidget(self.BtnConnect)
        self.BtnDisConnect = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.BtnDisConnect.setFont(font)
        self.BtnDisConnect.setAutoFillBackground(False)
        self.BtnDisConnect.setStyleSheet("QPushButton{ " + formatui)
        self.BtnDisConnect.setDefault(False)
        self.BtnDisConnect.setObjectName("BtnDisConnect")
        self.horizontalLayout.addWidget(self.BtnDisConnect)
        self.BtnArch = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.BtnArch.setFont(font)
        self.BtnArch.setAutoFillBackground(False)
        self.BtnArch.setStyleSheet("QPushButton{ " + formatui)
        self.BtnArch.setDefault(False)
        self.BtnArch.setObjectName("BtnArch")
        self.horizontalLayout.addWidget(self.BtnArch)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.tabLog = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        self.tabLog.setStyleSheet("QTableWidget{ background-color:  #03DAC5; color: black; border-style: outset; border-width: 2px; border-radius: 10px; border-color: beige; font: bold 12px; align: center;}")
        self.tabLog.setObjectName("tabLog")
        self.tabLog.setColumnCount(8)
        self.tabLog.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        # self.tabLog.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        heads = ['Sr.No.', 'Date', 'Start Time', 'Stop Time', 'Error Code', 'Type', 'Description', 'Status']
        self.tabLog.setHorizontalHeaderLabels(heads)


     
        self.gridLayout.addWidget(self.tabLog, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        #Display Comm messages
        self.text_edit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.text_edit.setFont(font)
        self.text_edit.setAutoFillBackground(False)
        self.text_edit.setObjectName("text_edit")
        self.verticalLayout.addWidget(self.text_edit)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


        # Connect buttons to functions
        self.BtnConnect.clicked.connect(self.start_client)
        self.BtnDisConnect.clicked.connect(self.stop_client)

        # self.BtnArch.clicked.connect(self.openLogFolder)



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Alarm Logging Tool", "Alarm Logging Tool"))
        self.label.setText(_translate("MainWindow", "Alarm Logging Tool"))
        self.label_2.setText(_translate("MainWindow", "IP"))
        self.label_3.setText(_translate("MainWindow", "Port"))
        self.BtnConnect.setText(_translate("MainWindow", "Connect"))
        self.BtnArch.setText(_translate("MainWindow", "OpenLogFolder"))

        self.client_thread = None

    def start_client(self):
        if not self.client_thread or not self.client_thread.is_alive():
            self.client_thread = ClientThread(host, port, self.text_edit)
            self.client_thread.start()
            self.BtnConnect.setEnabled(False)
            self.BtnDisConnect.setEnabled(True)

    def stop_client(self):
        if self.client_thread and self.client_thread.is_alive():
            self.client_thread.stop()
            self.client_thread.join()
            self.BtnConnect.setEnabled(True)
            self.BtnDisConnect.setEnabled(False)

class ClientThread(threading.Thread):
    def __init__(self, host, port, text_edit):
        super().__init__()
        self.host = host
        self.port = port
        self.text_edit = text_edit
        self.stop_event = threading.Event()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.port))
                while not self.stop_event.is_set():
                    data = s.recv(1024)
                    if not data:
                        break
                    message = data.decode("utf-8")
                    print(message)
                    self.text_edit.append(message)
            except Exception as e:
                self.text_edit.append(f"Error: {str(e)}")

    def stop(self):
        self.stop_event.set()
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
