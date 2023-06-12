from Modules import np
from GraphContainer import GraphContainer
from GraphCalculator import GraphCalculator

# Constructor Pattern
# Singleton Pattern
# Observer Pattern
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

    def plot2(self, fig):
        wav_range = np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), 1000)
        temps = np.linspace(float(self.parent.ui.TempStart.text()), float(self.parent.ui.TempEnd.text()), 7)  # Example temperatures
        ax = fig.add_subplot(111)
        for T in temps:
            intensity, peak_wav = self.graph_calculator.planck_wien(wav_range, T)

            ax.plot(wav_range, intensity, label=f'T = {T} K')

            max_intensity = np.max(intensity)
            max_wav = wav_range[np.argmax(intensity)]
            ax.axhline(y=max_intensity, color='r', linestyle='--', alpha=0.5)
            ax.axvline(x=max_wav, color='r', linestyle='--', alpha=0.5)

            ax.plot([peak_wav], [max_intensity], 'bo')
        ax.set_xlabel('длина волны')
        ax.set_ylabel('интенсивность')
        ax.set_title('закон Планка')
        ax.grid(True)
        ax.legend()

    def plot3(self, fig):
        wav_range = np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), 1000)
        temps = np.linspace(float(self.parent.ui.TempStart.text()), float(self.parent.ui.TempEnd.text()), 7)
        peak_wavs = [(1e-3) / T for T in temps]

        ax = fig.add_subplot(111)
        for i, temp in enumerate(temps):
            spectrum = self.graph_calculator.spectral_density(wav_range, temp)
            ax.plot(wav_range, spectrum, label=f'температура: {temp} K (Пик: {peak_wavs[i] * 1e6:.2f} мкм)')

        ax.set_xlabel('длина волны')
        ax.set_ylabel('Спектральная плотность')
        ax.set_title('Спектральная плотность энергетической светимости абсолютно черного тела')
        ax.grid(True)
        ax.legend()

