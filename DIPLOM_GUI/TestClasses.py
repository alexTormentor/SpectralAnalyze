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


class Receiver:
    def __init__(self, type_, diag, diameter, resist, darkness, coef_amp, length, dark_prov, width, size, delta, power):
        self.type = type_
        self.diag = diag
        self.diameter = diameter
        self.resist = resist
        self.darkness = darkness
        self.coef_amp = coef_amp
        self.length = length
        self.darkprov = dark_prov
        self.width = width
        self.size = size
        self.delta = delta
        self.power = power


class PlotData:
    def __init__(self, type_, data_func):
        self.type = type_
        self.data_func = data_func


class DatabaseManager:
    def __init__(self, database_name):
        self.database_name = database_name

    def execute_query(self, query):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def fetch_receiver_data(self):
        query = "SELECT Type, Diaphr, Diameter, Resist, DarkResist, CoeffAmpl, Length, DarkProv, Width, SizePh, Delta, Power FROM Receiver"
        return self.execute_query(query)

    def fetch_plot_data(self):
        query = "SELECT type FROM Plots"
        return self.execute_query(query)


def y(lambda_val, T):
    '''
    Безразмерная функция для расчёта закона Планка для абсолютно чёрного тела.

    Параметры:
    lambda_val (float): диапазон длин волн.
    T (float): значение температуры.

    Возвращаемое значение:
    result: безразмерная характеристика.
    '''
    c2 = (6.62607015e-34 * 2.99792458e8) / 3.3805e-23
    x = 4.9651 * ((lambda_val * T) / c2)
    exponent = np.exp(4.9651 / x)
    denominator = exponent - 1
    result = 142.32 * x ** -5 * denominator ** -1

    return result


class GraphManager:
    def __init__(self, parent):
        self.parent = parent
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout = QtWidgets.QVBoxLayout(self.parent.ui.PlotPlace)
        layout.addWidget(self.canvas)
        self.plot_button_pressed = False

    def update_plot(self, plot_func):
        if self.plot_button_pressed:
            self.fig.clear()
            plot_func(self.fig)
            self.canvas.draw()

    def update_receiver_fields(self, selected_type):
        self.parent.current_receiver = next(
            (receiver for receiver in self.parent.receiver_list if receiver.type == selected_type), None
        )
        if self.parent.current_receiver:
            self.calculate_radiance()

    def y(self, lambda_val, T):
        '''
        Безразмерная функция для расчёта закона Планка для абсолютно чёрного тела.

        Параметры:
        lambda_val (float): диапазон длин волн.
        T (float): значение температуры.

        Возвращаемое значение:
        result: безразмерная характеристика.
        '''
        c2 = (6.62607015e-34 * 2.99792458e8) / 3.3805e-23
        x = 4.9651 * ((lambda_val * T) / c2)
        exponent = np.exp(4.9651 / x)
        denominator = exponent - 1
        result = 142.32 * x ** -5 * denominator ** -1

        return result

    def calculate_radiance(self):
        wavelength = float(self.parent.ui.TargetWave.text())
        temperature = float(self.parent.ui.TargetTemp.text())

        radiance = self.y(wavelength, temperature)
        self.parent.ui.FluxValueOut.setText(str(radiance))


    def planck_wien(self, wav, T):
        '''
        Функция расчёта закона Планка для абсолютно чёрного тела.

        Параметры:
        wav (float): длина волны.
        T (float): значение температуры.

        Возвращаемое значение:
        intensity (float): распределение интенсивности.
        peak_wav (float): Пик интенсивности
        '''
        h = 6.62607015e-34
        c = 2.99792458e8
        k = 1.380649e-23

        b = h * c / (wav * k * T)
        intensity = (2.0 * h * c ** 2) / ((wav ** 5) * (np.exp(b) - 1.0))

        # пиковая длина волны с использованием закона Вина
        peak_wav = (2.897771955e-3) / T

        return intensity, peak_wav

    def plot3(self, fig):
        wav_range = np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), 1000)
        temperature = float(self.parent.ui.TargetTemp.text())

        intensity, peak_wav = self.planck_wien(wav_range, temperature)
        ax = fig.add_subplot(111)
        ax.plot(wav_range, intensity)
        ax.set_xlabel('длина волны')
        ax.set_ylabel('Интенсивность')
        ax.set_title('Закон Планка')
        ax.grid(True)

        # Add vertical line for the peak wavelength
        ax.axvline(x=peak_wav, color='r', linestyle='--', label='Пиковая длина волны')
        ax.legend()

    def display_selected_plot(self):
        selected_plot = self.parent.ui.PlotBox.currentText()
        if selected_plot == "график1":
            self.update_plot(self.plot1)
        elif selected_plot == "график2":
            self.update_plot(self.plot2)
        elif selected_plot == "график3":
            self.update_plot(self.plot3)
        self.plot_button_pressed = True

    def plot1(self, fig):
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax = fig.add_subplot(111)
        ax.plot(x, y)

    def plot2(self, fig):
        x = np.linspace(0, 10, 100)
        y = np.cos(x)
        ax = fig.add_subplot(111)
        ax.plot(x, y)


class PyShineLivePlotApp(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('ADSS.ui', self)
        self.resize(920, 740)

        self.threadpool = QtCore.QThreadPool()
        self.receiver_list = []
        self.plot_list = []

        # Additional fields
        self.current_receiver = None

        self.graph_manager = GraphManager(self)

        self.populate_receiver_list()
        self.update_receiver_combo_box()
        self.populate_plot_list()
        self.update_plot_combo_box()

        self.ui.ReceiverBox.currentTextChanged.connect(self.graph_manager.update_receiver_fields)
        self.ui.PlotGraph.clicked.connect(self.graph_manager.display_selected_plot)
        self.ui.Calculate.clicked.connect(self.graph_manager.calculate_radiance)

    def populate_receiver_list(self):
        db_manager = DatabaseManager('DIPLOM.db')
        receiver_data = db_manager.fetch_receiver_data()
        for row in receiver_data:
            receiver = Receiver(*row)
            self.receiver_list.append(receiver)

    def update_receiver_combo_box(self):
        self.ui.ReceiverBox.clear()
        for receiver in self.receiver_list:
            self.ui.ReceiverBox.addItem(receiver.type)
        self.graph_manager.update_plot(None)

    def update_plot_combo_box(self):
        self.ui.PlotBox.clear()
        for plot in self.plot_list:
            self.ui.PlotBox.addItem(plot.type)

    def populate_plot_list(self):
        db_manager = DatabaseManager('DIPLOM.db')
        plot_data = db_manager.fetch_plot_data()
        for row in plot_data:
            plot = PlotData(row[0], None)  # Add the data_func if needed
            self.plot_list.append(plot)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = PyShineLivePlotApp()
    window.show()
    app.exec_()