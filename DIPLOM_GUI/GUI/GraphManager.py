from Modules import np, scipy, QtCore
from GraphContainer import GraphContainer
from GraphCalculator import GraphCalculator
from DatabaseManager import DatabaseManager

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
        elif selected_plot == "график4":
            self.graph_container.update_plot(self.plot4)
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

    def plot4(self, fig):
        wav_range = np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), 1000)

        # Retrieve selected receiver and material
        selected_receiver = self.parent.ui.ReceiverBox.currentText()
        selected_material = self.parent.ui.MaterialBox.currentText()

        # Fetch sensitivity values for the selected receiver
        db_manager = DatabaseManager('../DIPLOM.db')
        query = f"SELECT Sensitivity FROM Receiver WHERE Type = '{selected_receiver}'"
        sensitivity_data = db_manager.execute_query(query)
        sensitivity_values = list(map(float, sensitivity_data[0][0].split(',')))

        # Fetch transmission values for the selected material
        query = f"SELECT Transmission FROM Materials WHERE Material = '{selected_material}'"
        transmission_data = db_manager.execute_query(query)
        transmission_values = list(map(float, transmission_data[0][0].split(',')))

        # Perform calculations and plotting
        trans_values = np.interp(wav_range, np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), len(transmission_values)), transmission_values)
        smoothed_trans_values = scipy.ndimage.gaussian_filter1d(trans_values, sigma=20)

        s_values = np.interp(wav_range, np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), len(sensitivity_values)), sensitivity_values)
        smoothed_s_values = scipy.ndimage.gaussian_filter1d(s_values, sigma=20)

        ax = fig.add_subplot(111)
        norm1 = smoothed_trans_values / np.max(smoothed_trans_values)
        norm3 = smoothed_s_values / np.max(smoothed_s_values)

        ax.plot(wav_range * 1e6, self.graph_calculator.y(wav_range, float(self.parent.ui.TargetTemp.text())), label='y(λ, T)')
        ax.plot(wav_range * 1e6, norm1, label='τ(λ)')
        ax.plot(wav_range * 1e6, norm3, label='s(λ)')

        ax.fill_between(wav_range * 1e6, np.minimum(self.graph_calculator.y(wav_range, float(self.parent.ui.TargetTemp.text())), norm1), color='gray',
                        alpha=0.3)
        ax.fill_between(wav_range * 1e6, np.minimum(self.graph_calculator.y(wav_range, float(self.parent.ui.TargetTemp.text())), norm3), color='black',
                        alpha=0.3)

        ax.set_xlabel('λ')
        ax.set_ylabel('нормализованное значение')
        ax.set_title('Спектральная характеристика')
        ax.legend()

        return fig





