# ----------------------------------------------------------------------
# Title: uart_driver.py
# Author: Ace Stratton
# Date: November 7th, 2023
# Description: Script that contains the functions for the UART driver
# class
# ----------------------------------------------------------------------

# Libraries ------------------------------------------------------------

# Local libraries
import serial
import serial.tools.list_ports as sp
import sys

class UART_Driver():
    """
    Class that encompasses all the functionalities required to send and 
    receive data over a single-ended UART bus

    Attributes
    ----------
    comm_ports_list : list
        List of available serial ports
    conn : Serial
        Serial connection object
    
    Methods
    ----------
    getAvailablePorts()
        Return a list of available serial ports
    open_conn(port)
        Open a serial connection
    close_conn()
        Close a serial connection
    clear_tx_buffer()
        Function to clear the UART transmission buffer
    clear_rx_buffer()
        Function to clear the UART reception buffer
    send_bytes(tx_buffer)
        Send bytes over serial port connection
    read_bytes(rx_len)
        Read bytes over serial port connection
    get_unread_bytes()
        Get the number of bytes in waiting in the RX buffer
    """

    def __init__(self, *args):
        """
		Constructor

		Parameters
		----------
		args : misc
			Miscellaneous parameters
		"""

         # Find and store list of available serial ports
        ports = sp.comports()
        self.comm_ports_list = []
        for p in ports:
            self.comm_ports_list.append(p.device)

    def getAvailablePorts(self):
        """
        Return a list of available serial ports
        """ 

        return self.comm_ports_list
    
    def open_conn(self, port):
        """
        Open a serial connection
        """

        try:
            self.conn = serial.Serial(port=port,
                                      baudrate=115200,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE,
                                      bytesize=serial.EIGHTBITS,
                                      timeout=0.2)
            return True
        except:
            print ("UART ERROR: Serial port '" + port + "' not open")
            return False
        
    def close_conn(self): 
       """
       Close a serial connection
       """

       try:
            self.conn.close()
       except:
            print("UART ERROR: Serial connection close failed")

    def clear_tx_buffer(self):
        """
        Function to clear the UART transmission buffer
        """

        try:
            self.conn.flushOutput()
        except:
            print("UART ERROR: Clear TX serial buffer failed")

    def clear_rx_buffer(self):
        """
        Function to clear the UART reception buffer
        """

        try:
            self.conn.flushInput()
        except:
            print("UART ERROR: Clear RX serial buffer failed")

    def send_bytes(self, tx_buffer):
        """
        Send bytes over serial port connection

        Parameters
        ----------
        tx_buffer : bytearray
            Byte array of hex values to send over serial
            (i.e. [0x35, 0x2E, 0xF8, 0x53])
        """
        try:
            self.clear_tx_buffer()
            self.conn.write(tx_buffer)
            self.clear_tx_buffer()
            return True
        except:
            return False
        
    def read_bytes(self, rx_len):
        """
        Read bytes over serial port connection

        Parameters
        ----------
        rx_len : int
            Number of bytes to read
        """  

        rx_stat = False
        rx_buf = []
        try:
            #if (self.conn.inWaiting() >= rx_len):
            rx_buf = self.conn.read(rx_len)                             # Blocks until requested number of bytes arrives or until read timeout specified in constructor (0.2 s)
            rx_buf = [b for b in rx_buf]
            rx_stat = True
        except:
            rx_stat = False
        return rx_stat, rx_buf

    def get_unread_bytes(self):
        """
        Get the number of bytes in waiting in the RX buffer
        """

        try:
            return self.conn.inWaiting()
        except:
            print("UART ERROR: Failed to get serial bytes in waiting")
            return -1

# ---------------------------------------------------------------------- 
