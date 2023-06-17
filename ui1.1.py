# -*- coding: utf-8 -*-


#importing all required libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, QDate, QTime,Qt
from PyQt5.QtCore import pyqtSlot
import requests
import pandas as pd
import json
from pandas import json_normalize
import datetime
import matplotlib.pyplot as plt
import seaborn as sns 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import entsoe_client as ec
from entsoe_client.ParameterTypes import *
from matplotlib.figure import Figure
import sys 
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import matplotlib.gridspec as gridspec
import os


class Ui_MainWindow(object):
    #function for the UI defining elements, their placements and functions 
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1426, 865)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        #creating a layout to place widgets in
        self.main_frrame = QtWidgets.QFrame(self.centralwidget)
        self.main_frrame.setGeometry(QtCore.QRect(19, 19, 1401, 811))
        self.main_frrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.main_frrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.main_frrame.setObjectName("main_frrame")
        
        #layout for the title on the UI
        self.title_frame = QtWidgets.QFrame(self.main_frrame)
        self.title_frame.setGeometry(QtCore.QRect(320, 0, 981, 81))
        self.title_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.title_frame.setObjectName("title_frame")
        
        self.label = QtWidgets.QLabel(self.title_frame)
        self.label.setGeometry(QtCore.QRect(14, 10, 961, 51))
        font = QtGui.QFont()
        font.setFamily("Sitka Text")
        font.setPointSize(22)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        self.options_frame = QtWidgets.QFrame(self.main_frrame)
        self.options_frame.setGeometry(QtCore.QRect(10, 110, 981, 101))
        self.options_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.options_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.options_frame.setObjectName("options_frame")
        
        #selection box for start date
        self.start_date = QtWidgets.QDateTimeEdit(self.options_frame)
        self.start_date.setGeometry(QtCore.QRect(20, 10, 194, 22))
        self.start_date.setDate(QtCore.QDate(2022, 12, 1))
        self.start_date.setTime(QtCore.QTime(22, 0, 0))
        self.start_date.setCalendarPopup(True)
        self.start_date.setObjectName("start_date")
        
        #selection box for end date
        self.End_date = QtWidgets.QDateTimeEdit(self.options_frame)
        self.End_date.setGeometry(QtCore.QRect(230, 10, 194, 22))
        self.End_date.setDate(QtCore.QDate(2022, 12, 2))
        self.End_date.setTime(QtCore.QTime(5, 0, 0))
        self.End_date.setCalendarPopup(True)
        self.End_date.setObjectName("End_date")
        
        #plot button to plot graphs uses the plotAll function which is defined later in the code
        self.plot_button = QtWidgets.QPushButton(self.options_frame)
        self.plot_button.setGeometry(QtCore.QRect(20, 50, 401, 41))
        self.plot_button.setObjectName("plot_button")
        self.plot_button.clicked.connect(self.plotAll)
        
        #button for saving the data in CSV format
        self.pushButton = QtWidgets.QPushButton(self.options_frame)
        self.pushButton.setGeometry(QtCore.QRect(510, 10, 181, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.save_stuff)
        
        #button to load previous data 
        self.pushButton_2 = QtWidgets.QPushButton(self.options_frame)
        self.pushButton_2.setGeometry(QtCore.QRect(510, 50, 181, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.loadStuff)
        
        self.graph3_frame = QtWidgets.QFrame(self.main_frrame)
        self.graph3_frame.setGeometry(QtCore.QRect(0, 240, 1381, 551))
        self.graph3_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.graph3_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.graph3_frame.setObjectName("graph3_frame")
        
        self.horizontalLayout3 = QtWidgets.QHBoxLayout(self.graph3_frame)
        self.horizontalLayout3.setObjectName('plot3Layout')
        
        self.fig1 = plt.figure()
        self.canvas1 = FigureCanvas(self.fig1)
        self.fig1.set_facecolor("green")
        
        self.horizontalLayout3.addWidget(self.canvas1, 0)
       
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Wind Energy Monitoring "))
        self.plot_button.setText(_translate("MainWindow", "Plot"))
        self.pushButton.setText(_translate("MainWindow", "Save"))
        self.pushButton_2.setText(_translate("MainWindow", "Load"))
    
    #---------------------------------------------------------Functions for API Data extraction-------------------------------------------------------------- 
    
    #function to get predicted energy production values from fingrid API
    def getPred_val(self):
        #formatting time to ISO
        TimeStart = self.start_date.dateTime()
        TimeEnd = self.End_date.dateTime()
        start_time = TimeStart.toString(format=Qt.ISODate)
        end_time = TimeEnd.toString(format=Qt.ISODate)
        
        #getting API response
        response = requests.get(f"https://api.fingrid.fi/v1/variable/245/events/json",
        headers={
            'x-api-key': ''
   
        },
        params ={
                'start_time': start_time+'+0000', #adding +0000 so that it is in the format required by the API
                'end_time': end_time+'+0000'
        }          
        )
        #converting data obtained to json 
        data = response.json()
        
        #converting json response to pandas dataframe
        df1 = pd.json_normalize(data) 
        return df1
    
    #function to get real wind energy production from fingrid API
    def getRealProd(self):
        TimeStart = self.start_date.dateTime()
        TimeEnd = self.End_date.dateTime()
        start_time = TimeStart.toString(format=Qt.ISODate)
        end_time = TimeEnd.toString(format=Qt.ISODate)
        response = requests.get(f"https://api.fingrid.fi/v1/variable/75/events/json",
         headers={
            'x-api-key': '' #enter API key here
   
        },
        params ={
                'start_time': start_time+'+0000',
                'end_time': end_time+'+0000'
        }          
        )
        data = response.json()

        df2 = pd.json_normalize(data)
        return df2

    #function to get day ahead energy prices using entsoe API
    def getEntsoe(self):
        TimeStart = self.start_date.dateTime()
        TimeEnd = self.End_date.dateTime()
        start_time = TimeStart.toString(format=Qt.ISODate)
        end_time = TimeEnd.toString(format=Qt.ISODate)
        client = ec.Client('') #enter api key here
        parser = ec.Parser
        predefined_query = ec.Queries.Transmission.DayAheadPrices(
            in_Domain ="10YCZ-CEPS-----N" ,  #search entsoe API to get the code for the required data. For day ahead prices of wind energy it is the one mentioned here
            periodStart= start_time,
            periodEnd=end_time
            )
        #using entsoe client library to parse through the response and convert it into a pandas dataframae
        response = client(predefined_query)
        df = parser.parse(response)
        print(df.index)
        return df
        

#------------------------------------------------------------------------------Function for plotting graphs------------------------------------------------------------------------------------


    def plotAll(self):
       self.fig1.clf()
       a = self.getPred_val()
       b = self.getRealProd()
       c = self.getEntsoe()
       
       timeArray_a = pd.to_datetime(a["start_time"])
       timeArray_b = pd.to_datetime(b["start_time"])
       c["price.amount"] = c["price.amount"].astype(float)
       c["Date_info"] = c.index
    

       gs = gridspec.GridSpec(2, 2)

       fig = plt.figure()
       ax1 = self.fig1.add_subplot(gs[0, 0]) # row 0, col 0
       ax1.plot(timeArray_a, a["value"])
       ax1.tick_params(axis='x', rotation = 15) 
       ax1.set_ylabel('mWh')
       ax1.grid()
       

       ax2 = self.fig1.add_subplot(gs[0, 1]) # row 0, col 1
       ax2.plot(timeArray_b, b["value"])
       ax2.tick_params(axis='x', rotation = 15)
       ax2.set_ylabel('mWh')
       ax2.grid()

       ax3 = self.fig1.add_subplot(gs[1, :]) # row 1, span all columns
       ax3.plot(c["Date_info"] , c["price.amount"])
       ax3.plot(timeArray_b, b["value"])
       ax3.set_ylabel('€/mWh')
       ax3.grid()
       self.canvas1.draw()



    #function to save the data obtained from all the API's in a single .csv file for later use and analysis
    def save_stuff(self):
        a = self.getPred_val()
        b = self.getRealProd()
        c = self.getEntsoe()
        c["Date_info"] = c.index
        c.drop("position", inplace=True, axis=1)

    
        pdList = [c, b, a] 
        df = pd.concat(pdList, axis="columns")

        TimeStart = self.start_date.dateTime()
        TimeEnd = self.End_date.dateTime()
        start_time = TimeStart.toString(format=Qt.ISODate)
        end_time = TimeEnd.toString(format=Qt.ISODate)
    
        #d = pd.concat([a, b], axis="columns")
        #e = pd.concat([d, c], axis="columns")
       
       
        name1 = str(start_time)+'to'+str(end_time)
        name2 = name1.replace(':','_')
        df.to_csv(f'C://Animesh//Python Project 2022//Saved_stuff//{name2}.csv', index=True)  #enter filepath here for saving the data obtained 


    #function to access the saved data and plot it
    def loadStuff(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()
        self.fig1.clf()
        df = pd.read_csv(str(filename[0]), delimiter=',')
        print(list(df.columns))
        timeArray_1 = pd.to_datetime(df["start_time"])
        timeArray_2 = pd.to_datetime(df["start_time.1"])
        df["price.amount"] = df["price.amount"].astype(float)
        
        gs = gridspec.GridSpec(2, 2)

       
        ax1 = self.fig1.add_subplot(gs[0, 0]) # row 0, col 0
        ax1.plot(timeArray_1, df["value"])
        ax1.tick_params(axis='x', rotation = 15) 
        ax1.set_ylabel('mWh')
        ax1.grid()
       

        ax2 = self.fig1.add_subplot(gs[0, 1]) # row 0, col 1
        ax2.plot(timeArray_2, df["value.2"])
        ax2.tick_params(axis='x', rotation = 15)
        ax2.set_ylabel('mWh')
        ax2.grid()

        ax3 = self.fig1.add_subplot(gs[1, :]) # row 1, span all columns
        ax3.plot(df["Date_info"] , df["price.amount"])
        ax3.set_ylabel('€/mWh')
        ax3.grid()
        self.canvas1.draw() #plotting all subplots on the same canvas


        
        
        





        











if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
