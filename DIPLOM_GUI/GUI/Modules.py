import sys
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import queue
import pdb
from functools import reduce
import operator
import random
import math
import scipy
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp2d, interp1d
from scipy.integrate import trapz, quad, simps
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
import sqlite3
