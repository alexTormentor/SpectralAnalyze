from Modules import np
from GraphContainer import GraphContainer
from GraphCalculator import GraphCalculator

class GraphManager:
    def __init__(self, parent):
        self.parent = parent
        self.graph_calculator = GraphCalculator()
        self.graph_container = GraphContainer(self.parent)

    def update_receiver_fields(self, selected_type):
        self.parent.current_receiver = next(
            (receiver for receiver in self.parent.receiver_list if receiver.type == selected_type), None
        )


    def calculate_variables(self):
        if self.parent.current_receiver:
            wavelength = float(self.parent.ui.TargetWave.text())
            temperature = float(self.parent.ui.TargetTemp.text())

            radiance = self.graph_calculator.y(wavelength, temperature)
            formatted_radiance = "{:.3f}".format(radiance)
            # Calculate other variables here
            # variable1 = ...
            # variable2 = ...
            # ...

            # Update the UI with the calculated variables
            self.parent.ui.FluxValueOut.setText(str(formatted_radiance))
            # Update other UI elements with the calculated variables
            # self.parent.ui.Variable1Label.setText(str(variable1))
            # self.parent.ui.Variable2Label.setText(str(variable2))
            # ...

    def calculate_radiance(self):
        self.calculate_variables()

    def display_selected_plot(self):
        selected_plot = self.parent.ui.PlotBox.currentText()
        if selected_plot == "график1":
            self.graph_container.update_plot(self.plot1)
        elif selected_plot == "график2":
            self.graph_container.update_plot(self.plot2)
        elif selected_plot == "график3":
            self.graph_container.update_plot(self.plot3)
        self.graph_container.plot_button_pressed = True

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

    def plot3(self, fig):
        wav_range = np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), 1000)
        temperature = float(self.parent.ui.TargetTemp.text())
        intensity, peak_wav = self.graph_calculator.planck_wien(wav_range, temperature)
        ax = fig.add_subplot(111)
        ax.plot(wav_range, intensity)
        ax.set_xlabel('длина волны')
        ax.set_ylabel('Интенсивность')
        ax.set_title('Закон Планка')
        ax.grid(True)
        ax.axvline(x=peak_wav, color='r', linestyle='--', label='Пиковая длина волны')
        ax.legend()
