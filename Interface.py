import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5Agg backend for matplotlib
import numpy as np
import pandas as pd

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QFileDialog, QInputDialog

from MplCanvas import MplCanvas


class MainWindow(QtWidgets.QMainWindow):
    """
    Main window class that inherits from QtWidgets.QMainWindow. It sets up the main
    GUI for displaying plots and interacting with the user to load and customize plots.
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes the main window, sets up the canvas for displaying plots,
        and adds a button to trigger the plot loading process.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # Initialize the canvas for plotting
        self.canvas = MplCanvas(parent=self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)  # Set the canvas as the central widget
        self.setGeometry(700, 300, 1000, 1000)  # Set initial size and position of the window

        # Button to add a new plot
        self.button = QPushButton("add plot", self)
        self.initUI()  # Initialize the user interface
    
    def initUI(self):
        """
        initializes the user interface, including button styling and connections.
        Sets up the button to trigger the `new_plot` method when clicked.
        """
        # Set button geometry (position and size) and style
        self.button.setGeometry(10, 10, 200, 100)
        self.button.setStyleSheet("font-size: 30px;")  # Set button font size
        self.button.clicked.connect(self.new_plot)  # Connect button click to the `new_plot` method
    
    def new_plot(self):
        """
        handles the "add plot" button click event. Prompts the user to select a CSV
        file for plotting and then processes the data accordingly.
        opens a file dialog to select a CSV file, then calls the method to parse
        and process the data.
        """
        print('clicked')  # For debugging purposes, prints when the button is clicked
        # Open file dialog to select a CSV file
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if file_name:
            self.__parse_data(file_name)  # Parse the data if a file is selected
    
    def __parse_data(self, file_name):
        """
        Parses the selected CSV file, asks the user for plot-related inputs,
        and adds the plot to the canvas.

        Args:
            file_name (str): The path to the selected CSV file.
        """
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_name)
        
        # Ask the user for the plot title
        plot_name, ok = QInputDialog.getText(self, 'Plot Title', 'Enter a title for the plot:')
        if not ok:  # If the user cancels, stop further execution
            return
        
        # Ask if the data is paired or not
        paired, ok = QInputDialog.getItem(self, 'Paired Data', 'Is this paired data?', ['Yes', 'No'], 0, False)
        paired = 1 if paired == 'Yes' else 0  # Convert user selection to binary

        # Ask for the plot type (either Straight Line or Scatter)
        plot_type, ok = QInputDialog.getItem(self, 'Plot Type', 'Choose plot type:', ['Straight Line', 'Scatter'], 0, False)
        plot_type = 0 if plot_type == 'Straight Line' else 1  # Convert to integer

        # Add the plot to the canvas using the user-provided information
        self.canvas.add_plot(plot_name, df, paired, plot_type)


if __name__ == "__main__":
    """
    Main entry point for the application. Initializes the application, creates
    the main window, and starts the Qt event loop.
    """
    # Create the QApplication instance, which manages application-wide resources
    app = QApplication(sys.argv)
    
    # Create and show the main window
    w = MainWindow()
    w.show()
    
    # Start the Qt event loop and exit cleanly when done
    sys.exit(app.exec_())
