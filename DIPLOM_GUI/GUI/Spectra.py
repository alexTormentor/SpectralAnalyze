from Modules import *
from GraphManager import GraphManager
from DatabaseManager import DatabaseManager
from PlotData import PlotData
from Receiver import Receiver

# Constructor Pattern
class Spectra(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi('../ADSS.ui', self)
        self.resize(920, 740)

        self.threadpool = QtCore.QThreadPool()
        self.receiver_list = []
        self.plot_list = []
        self.material_list = []
        self.current_receiver = None

        self.graph_manager = GraphManager(self)

        self.populate_receiver_list()
        self.update_receiver_combo_box()
        self.populate_plot_list()
        self.update_plot_combo_box()
        self.populate_material_list()  # Added method call
        self.update_material_combo_box()  # Added method call

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
        self.graph_manager.graph_container.update_plot(None)

    def update_plot_combo_box(self):
        self.ui.PlotBox.clear()
        for plot in self.plot_list:
            self.ui.PlotBox.addItem(plot.type)

    def populate_plot_list(self):
        db_manager = DatabaseManager('../DIPLOM.db')
        plot_data = db_manager.fetch_plot_data()
        for row in plot_data:
            plot_type = row[0]
            if plot_type == 'график1':
                self.plot_list.append(PlotData(plot_type, self.graph_manager.plot1))
            elif plot_type == 'график2':
                self.plot_list.append(PlotData(plot_type, self.graph_manager.plot2))
            elif plot_type == 'график3':
                self.plot_list.append(PlotData(plot_type, self.graph_manager.plot3))
            elif plot_type == 'график4':
                self.plot_list.append(PlotData(plot_type, self.graph_manager.plot4))

    def populate_material_list(self):
        db_manager = DatabaseManager('../DIPLOM.db')
        material_data = db_manager.fetch_material_data()  # Assuming there's a method to fetch material data
        for row in material_data:
            material = row[0]
            self.material_list.append(material)

    def update_material_combo_box(self):
        self.ui.MaterialBox.clear()
        for material in self.material_list:
            self.ui.MaterialBox.addItem(material)