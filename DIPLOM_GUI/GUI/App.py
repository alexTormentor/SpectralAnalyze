from Modules import *
from DatabaseManager import DatabaseManager
from GraphManager import GraphManager
from Receiver import Receiver
from PlotData import PlotData


class PyShineLivePlotApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('ADSS.ui', self)
        self.resize(920, 740)
        self.threadpool = QtCore.QThreadPool()
        self.receiver_list = []
        self.plot_list = []
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
        db_manager = DatabaseManager('../DIPLOM.db')
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
        db_manager = DatabaseManager('../DIPLOM.db')
        plot_data = db_manager.fetch_plot_data()
        for row in plot_data:
            plot = PlotData(row[0], None)  # Add the data_func if needed
            self.plot_list.append(plot)
