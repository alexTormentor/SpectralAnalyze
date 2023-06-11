import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import queue
import numpy as np
import pdb

from functools import reduce
import operator
import random
import math
import scipy
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp2d, interp1d
from scipy.integrate import trapz, quad, simps
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal, QObject
import sqlite3


class MplCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		super(MplCanvas, self).__init__(fig)
		fig.tight_layout()

class SignalEmitter(QObject):
    receiver_list_updated = pyqtSignal(list)

class PyShine_LIVE_PLOT_APP(QtWidgets.QMainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.ui = uic.loadUi('ADSS.ui', self)
		self.resize(920, 740)
		#icon = QtGui.QIcon()
		#icon.addPixmap(QtGui.QPixmap("PyShine.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		#self.setWindowIcon(icon)
		self.threadpool = QtCore.QThreadPool()
		self.receiver_list = []
		self.plot_list = []

		# Additional fields
		self.Diag = 0.0
		self.Diameter = 0.0
		self.Resist = 0.0
		self.Darkness = 0.0
		self.CoefAmp = 0.0
		self.Length = 0.0
		self.Darkprov = 0.0
		self.Width = 0.0
		self.Size = 0.0
		self.Delta = 0.0
		self.Power = 0.0

		# Create a Figure and a FigureCanvas
		self.fig = Figure()
		self.canvas = FigureCanvas(self.fig)

		# Add the FigureCanvas to the PlotPlace widget
		layout = QtWidgets.QVBoxLayout(self.ui.PlotPlace)
		layout.addWidget(self.canvas)


		self.populate_receiver_list()
		self.update_receiver_combo_box()
		self.populate_plot_list()
		self.update_plot_combo_box()

		self.ui.ReceiverBox.currentTextChanged.connect(self.update_receiver_fields)
		# Connect the PlotGraph button signal to the method that displays the selected plot
		self.ui.PlotGraph.clicked.connect(self.display_selected_plot)

		print(self.Diag)
		self.ui.FluxValueOut.setText(str(self.Diag))
		#print(self.Diag)

	def populate_receiver_list(self):
		# Create a connection to the SQLite database
		conn = sqlite3.connect('DIPLOM.db')
		cursor = conn.cursor()

		# Fetch the values from the "Type" column of the "Receiver" table
		cursor.execute(
			"SELECT Type, Diaphr, Diameter, Resist, DarkResist, CoeffAmpl, Length, DarkProv, Width, SizePh, Delta, Power FROM Receiver")
		receiver_data = cursor.fetchall()

		# Append the values to the receiver_list
		for row in receiver_data:
			type_ = row[0]
			self.receiver_list.append(type_)

		# Close the cursor and connection
		cursor.close()
		conn.close()

	def update_receiver_combo_box(self):
		# Clear the existing items in the comboBox
		self.ui.ReceiverBox.clear()

		# Add the values from the receiver_list to the comboBox
		self.ui.ReceiverBox.addItems(self.receiver_list)
		self.update_plot()

	def update_plot(self):
		# Clear the previous plot
		self.fig.clear()

		# Generate some sample data for the plot
		x = np.linspace(0, 10, 100)
		y = np.sin(x)

		# Create a new plot
		ax = self.fig.add_subplot(111)
		ax.plot(x, y)

		# Refresh the canvas
		self.canvas.draw()

	def update_plot2(self):
		# Clear the previous plot
		self.fig.clear()

		# Generate some sample data for the plot
		x = np.linspace(0, 10, 100)
		y = np.cos(x)

		# Create a new plot
		ax = self.fig.add_subplot(111)
		ax.plot(x, y)

		# Refresh the canvas
		self.canvas.draw()

	def update_receiver_fields(self, selected_type):
		# Create a connection to the SQLite database
		conn = sqlite3.connect('DIPLOM.db')
		cursor = conn.cursor()

		# Fetch the values for the selected "Type" from the "Receiver" table
		cursor.execute(
			"SELECT Diaphr, Diameter, Resist, DarkResist, CoeffAmpl, Length, DarkProv, Width, SizePh, Delta, Power FROM Receiver WHERE Type = ?",
			(selected_type,))
		row = cursor.fetchone()

		if row is not None:
			self.Diag = float(row[0])
			self.Diameter = float(row[1])
			self.Resist = float(row[2])
			self.Darkness = float(row[3])
			self.CoefAmp = float(row[4])
			self.Length = float(row[5])
			self.Darkprov = float(row[6])
			self.Width = float(row[7])
			self.Size = float(row[8])
			self.Delta = float(row[9])
			self.Power = float(row[10])

			# Update the corresponding line edits with the new values
			self.ui.FluxValueOut.setText(str(self.Diag + self.Resist))

		# Close the cursor and connection
		cursor.close()
		conn.close()

	def display_selected_plot(self):
		# Get the selected plot type from the comboBox
		selected_plot = self.ui.PlotBox.currentText()

		if selected_plot == "график1":
			self.update_plot()
		elif selected_plot == "график2":
			self.update_plot2()

	def update_plot_combo_box(self):
		# Clear the existing items in the comboBox
		self.ui.PlotBox.clear()

		# Add the values from the plot_list to the comboBox
		self.ui.PlotBox.addItems(self.plot_list)

	def populate_plot_list(self):
		# Create a connection to the SQLite database
		conn = sqlite3.connect('DIPLOM.db')
		cursor = conn.cursor()

		# Fetch the values from the "Type" column of the "Plots" table
		cursor.execute("SELECT type FROM Plots")
		plot_data = cursor.fetchall()

		# Append the values to the plot_list
		for row in plot_data:
			type_ = row[0]
			self.plot_list.append(type_)

		# Close the cursor and connection
		cursor.close()
		conn.close()







class Worker(QtCore.QRunnable):

	def __init__(self, function, *args, **kwargs):
		super(Worker, self).__init__()
		self.function = function
		self.args = args
		self.kwargs = kwargs

	@pyqtSlot()
	def run(self):

		self.function(*self.args, **self.kwargs)


app = QtWidgets.QApplication(sys.argv)
mainWindow = PyShine_LIVE_PLOT_APP()
mainWindow.show()
sys.exit(app.exec_())