# ----------------------------------------------------------------------
# Title: FOXSIPADRE_GUI.py
# Author: Ace Stratton
# Date: November 7th, 2023
# Descripcion: Main screen of FOXSI/PADRE GUI
# ----------------------------------------------------------------------

# Libraries ------------------------------------------------------------

# Local libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QMutex, QDateTime, QDate, QTime
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget
from datetime import datetime
from collections import deque
import pyqtgraph as pg
import time
import csv
import sys
import os

# Third-party libraries
from scipy.fft import rfft, rfftfreq
import matplotlib.pyplot as plt
import numpy as np
import pathlib

# Own libraries
from Qt_Main import Ui_MainWindow


# **********************************************************************
#                         MAIN SCREEN CLASS
# **********************************************************************

# Main screen inherits from QMainWindow and Ui_MainWindow (Qt Designer)
class Main_Screen(QtWidgets.QMainWindow, Ui_MainWindow):
    
    """
	Class that encompasses the functionalities of the main screen of the
    PLD GUI.

	Attribute
	----------
    config_data : list
        List used to store incoming PLD configuration table
    debug_data : list
        List used to store incoming PLD debugging data
    hk_auto_request_freq : int
        Seconds to wait between automatic retrievals of housekeeping 
        data from PLD instrument
    hk_data : list
        List used to store incoming PLD housekeeping data
    hk_filepath : str
        Filepath for the CSV used to save housekeeping data during a 
        test
    log_rx_filepath : str
        Filepath for the TXT used to save received responses logs 
        during a test
    log_tx_filepath : str
        Filepath for the TXT used to save transmitted commands logs 
        during a test
    sci_data_count : int
        Number of received PLD science data packets during timed
        recording
    sci_data : list
        List used to store incoming PLD science data
    sci_filepath : str
        Filepath for the CSV used to save science data during a test
    sci_mag_out_nT : bool
		Flag to indicate if instrument is outputting magnetic data or 
        not
    sci_streaming : bool
        Flag to indicate if instrument is streaming data back to GUI
	serial_open : bool
		Flag to indicate if UART connection has been initialized or not
    threadpool : QThreadpool
        Pool of threads used to store all asynchronous communication
        threads created during runtime
    uart_driver : UART_Driver
        Instance of UART_Driver object that contains the opened UART
        connection object and all functionalities to execute serial
        communication through it
    gui_decoder : GUI_Decoder
        Instance of GUI_Decoder object that contains all
        functionalities to parse the data received from the PLD
        instrument through the PLD interface
    gui_iface : GUI_Interface
        Instance of GUI_Interface object that contains all
        functionalities to send a valid command to the PLD
        instrument through the initialized UART driver

	Methods
	-------
    init_graphics()
        Initialize all variables used for graphical aesthetic 
        configuration
    init_ports()
        Find available serial ports and list them in the ports comboBox
    init_logger()
        Initialize the CSV file for data logging
    connect_slots()
        Connect signals to pushButton actions
    init_plots()
        Initialize all dynamic plots used to displace real-time data
    setErrorFlags(flag_no, status)
        Set value of error flag
    init_serial()
        Initialize serial connection
    reset_serial()
        Reset serial connection
    getHousekeepingPacket()
        Retrieve housekeeping data from the PLD instrument
    getHousekeepingPacketCallback(data)
        Process PLD housekeeping data received through 
        asynchronous serial interface
    printHousekeepingPacket()
        Display the housekeeping packet received
    toggleAutoHKRequest(isChecked)
        Toggle automatic retrieval of housekeeping data from the PLD 
        instrument
    setAutoHKRequestFreq(freq)
        Set frequency for automatic retrieval of housekeeping data from 
        the PLD instrument
    setAnalogBoardControl()
        Control the PLD +5V and -5V rails for the Analog Board 
        (enable/disable)
    setInstrument1Control()
        Control the PLD Instrument Board No.1 (enable/disable)
    setInstrument2Control()
        Control the PLD Instrument Board No.2 (enable/disable)
    setNST1Control()
        Control the PLD Star Tracker No.1 (enable/disable)
    setNST2Control()
        Control the PLD Star Tracker No.2 (enable/disable)
    setControlCallback(data, action)
        Callback for the enable and disable functionalities
    setTimeOfTone()
        Send time of tone to PLD instrument
    setTimeOfToneCallback(data)
        Callback for the PLD update Time of Tone functionality
    setConfigurationTable()
        Send new Configuration Table to the PLD instrument
    setDefaultConfigurationTable()
        Send default Configuration Table to the PLD instrument
    setConfigurationTableCallback(data)
        Callback for the update PLD Configuration Table functionality
    getConfigurationTable()
        Request PLD Configuration Table from the PLD instrument
    setDefaultConfigurationTable()
        Send default Configuration Table to the PLD instrument
    setConfigurationTableCallback(data)
        Callback for the update PLD Configuration Table functionality
    getConfigurationTable()
        Request PLD Configuration Table from the PLD instrument
    getConfigurationTableCallback(data)
        Process PLD Configuration table received through 
        asynchronous serial interface
    printConfigurationTable()
        Display the configuration table received
    getSciencePacket()
        Retrieve science data from the PLD instrument
    getSciencePacketCallback(data)
        Process PLD science data received through asynchronous 
        serial interface
    printSciencePacket()
        Display the housekeeping packet received
    setScienceControl()
        Control the PLD science stream (enable/disable)
    sendInstrumentPassThrough()
        Send command directly to instrument
    sendInstrumentPassThroughCallback()
        Callback for transmission of command directly to instrument
    getDebuggingPacket()
        Retrieve debugging data from the PLD instrument
    getDebuggingPacketCallback()
        Process PLD debugging data received through asynchronous 
        serial interface
    printDebuggingPacket()
        Display the debugging packet received
	"""

    def __init__(self, *args, parent=None):
        """
		Constructor

		Parameters
		----------
		args : misc
			Miscellaneous parameters
		parent : None
			Parent class of window
		"""


        QtWidgets.QMainWindow.__init__(self, parent)

        # Static configuration of MainWindow
        #copy paste this
        self.setupUi(self)
        #self.setStyleSheet("#MainWindow { border-image: url(./resources/gray_background.jpg) 0 0 0 0 stretch stretch; }")
        self.windows_icon = QtGui.QIcon('./resources/padre-logo_ucb.png')
        self.setWindowIcon(self.windows_icon)
        self.setWindowTitle("FOXSI/PADRE Timepix Visualizer")
        self.showMaximized()


        return
    
    def init_graphics(self):
        """
        Initialize all variables used for graphical aesthetic 
        configuration
        """

        # PyQT Graph Configuration
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', '#B3B3B3')

        # PyQT graphics color configuration
        red = pg.hsvColor(0.000,1.0,1.0)
        yellow = pg.hsvColor(0.167,1.0,1.0)
        green = pg.hsvColor(0.333,1.0,1.0)
        cyan = pg.hsvColor(0.500,1.0,1.0)
        blue = pg.hsvColor(0.667,1.0,1.0)
        magenta = pg.hsvColor(0.833,1.0,1.0)
        orange = pg.hsvColor(0.083,1.0,1.0)
        self.red_pen = pg.mkPen(color = red,width = 4.5)
        self.red_pen_fine = pg.mkPen(color = red,width = 1.5,style=QtCore.Qt.DashLine)
        self.yellow_pen = pg.mkPen(color = yellow,width = 4.5)
        self.green_pen = pg.mkPen(color = green,width = 4.5)
        self.green_pen_fine = pg.mkPen(color = green,width = 1.5,style=QtCore.Qt.DashLine)
        self.cyan_pen = pg.mkPen(color = cyan,width = 4.5)
        self.cyan_pen_fine = pg.mkPen(color = cyan,width = 2.5)
        self.blue_pen = pg.mkPen(color = blue,width = 4.5)
        self.blue_pen_fine = pg.mkPen(color = blue,width = 1.5)
        self.magenta_pen = pg.mkPen(color = magenta,width = 4.5)
        self.orange_pen = pg.mkPen(color = orange,width = 4.5)

