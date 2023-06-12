from Modules import Figure, FigureCanvas, QtWidgets

# Constructor Pattern
class GraphContainer:
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
