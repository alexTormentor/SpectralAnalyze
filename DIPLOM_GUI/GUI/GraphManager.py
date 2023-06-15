from Modules import np, scipy, QtCore, trapz, simps
from GraphContainer import GraphContainer
from GraphCalculator import GraphCalculator
from DatabaseManager import DatabaseManager
from Receiver import Receiver

# Constructor Pattern
# Singleton Pattern
# Observer Pattern
class GraphManager:
    def __init__(self, parent):
        self.parent = parent
        self.graph_calculator = GraphCalculator()
        self.graph_container = GraphContainer(self.parent)
        self.q = 0
        self.D = 0
        self.f = 0
        self.R_H = 0
        self.R_i = 0
        self.R_amp = 0
        self.d = 0
        self.H = 0
        self.l = 0
        self.delta = 0
        self.V = 0
        self.prov = 0

    def update_receiver_fields(self, selected_type):
        self.parent.current_receiver = next(
            (receiver for receiver in self.parent.receiver_list if receiver.type == selected_type), None
        )
        if self.parent.current_receiver:
            self.q = float(self.parent.current_receiver.diag)
            self.D = float(self.parent.current_receiver.diameter)
            self.f = float(self.parent.current_receiver.focus)
            self.R_H = float(self.parent.current_receiver.resist)
            self.R_i = float(self.parent.current_receiver.darkness)
            self.R_amp = float(self.parent.current_receiver.coef_amp)
            self.d = float(self.parent.current_receiver.width)
            self.H = float(self.parent.current_receiver.size)
            self.l = float(self.parent.current_receiver.length)
            self.delta = float(self.parent.current_receiver.delta)
            self.V = float(self.parent.current_receiver.power)
            self.prov = float(self.parent.current_receiver.darkprov)
        else:
            self.q = 0
            self.D = 0
            self.f = 0
            self.R_H = 0
            self.R_i = 0
            self.R_amp = 0
            self.d = 0
            self.H = 0
            self.l = 0
            self.delta = 0
            self.V = 0
            self.prov = 0


    def calculate_variables(self):
        if self.parent.current_receiver:
            wavelength = float(self.parent.ui.TargetWave.text())
            temperature = float(self.parent.ui.TargetTemp.text())
            lambda_1 = float(self.parent.ui.WaveStart.text())  # Lower limit of the integral
            lambda_2 = float(self.parent.ui.WaveEnd.text())  # Upper limit of the integral
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
            trans_values = np.interp(wav_range, np.linspace(float(self.parent.ui.WaveStart.text()),
                                                            float(self.parent.ui.WaveEnd.text()),
                                                            len(transmission_values)), transmission_values)

            s_values = np.interp(wav_range, np.linspace(float(self.parent.ui.WaveStart.text()),
                                                        float(self.parent.ui.WaveEnd.text()),
                                                        len(sensitivity_values)), sensitivity_values)

            a = self.q / 4
            b = self.D / self.f
            s_max = np.max(s_values)


            # Calculate other variables here
            integrand = trans_values * self.graph_calculator.spectral_density(wav_range, temperature)
            lambda_range = np.logical_and(wav_range >= lambda_1, wav_range <= lambda_2)
            selected_integrand = integrand[lambda_range]
            integral_value = simps(selected_integrand, wav_range[lambda_range])
            result = a * b**2 * integral_value
            formatted_result = "{:.5f}".format(result)

            integrand2 = s_values * trans_values * self.graph_calculator.spectral_density(wav_range, temperature)
            selected_integrand2 = integrand2[lambda_range]
            integral_value2 = simps(selected_integrand2, wav_range[lambda_range])
            result2 = a * b**2 * ((s_max * self.R_H * self.R_i * self.R_amp) / (self.R_H + self.R_i)) * integral_value2
            formatted_result2 = "{:.5f}".format(result2)

            IF2 = self.delta * ((self.d * self.H) / self.l) * self.V
            formatted_If2 = "{:.5f}".format(IF2)

            summaryCurrent = IF2 + self.prov
            formatted_SumCur = "{:.5f}".format(summaryCurrent)

            monochrome = IF2 / result
            formatted_monochrome = "{:.5f}".format(monochrome)


            # variable1 = ...
            # variable2 = ...
            # ...

            # Update the UI with the calculated variables
            # Update other UI elements with the calculated variables
            self.parent.ui.FluxValueOut.setText(str(formatted_result))
            self.parent.ui.PowerOut.setText(str(formatted_result2))
            self.parent.ui.FluxOut.setText(str(formatted_If2))
            self.parent.ui.SummaryCurrent.setText(str(formatted_SumCur))
            self.parent.ui.Monochromatic.setText(str(formatted_monochrome))
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
        elif selected_plot == "график5":
            self.graph_container.update_plot(self.plot5)
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


    def plot5(self, fig):
        ax = fig.add_subplot(111)

        wav_range = np.linspace(float(self.parent.ui.WaveStart.text()), float(self.parent.ui.WaveEnd.text()), 1000)
        # Retrieve selected receiver and material
        selected_receiver = self.parent.ui.ReceiverBox.currentText()
        selected_material = self.parent.ui.MaterialBox.currentText()


        temperature = float(self.parent.ui.TargetTemp.text())
        intensity, peak_wav = self.graph_calculator.planck_wien(wav_range, temperature)

        # Fetch sensitivity values for the selected receiver
        db_manager = DatabaseManager('../DIPLOM.db')

        max_index = np.argmax(self.graph_calculator.y(wav_range, temperature))
        a = wav_range[0]
        b = 0
        c = 0
        threshold = 0.98 * self.graph_calculator.y(wav_range, temperature)[max_index]
        for i in range(max_index, 0, -1):
            if self.graph_calculator.y(wav_range, temperature)[i] <= threshold:
                b = wav_range[i]
                break
        for i in range(max_index, len(wav_range)):
            if self.graph_calculator.y(wav_range, temperature)[i] <= threshold:
                c = wav_range[i]
                break
        d = wav_range[-1]

        membership_points_y = {'a': a, 'b': b, 'c': c, 'd': d}
        query = f"SELECT Membership FROM Materials WHERE Material = '{selected_material}'"
        transmission_data = db_manager.execute_query(query)
        transmission_values = list(map(float, transmission_data[0][0].split(',')))

        membership_points_transmission = {'a': transmission_values[0], 'b': transmission_values[1], 'c': transmission_values[2], 'd': transmission_values[3]}

        query = f"SELECT Membership FROM Receiver WHERE Type = '{selected_receiver}'"
        s_data = db_manager.execute_query(query)
        s_values = list(map(float, s_data[0][0].split(',')))

        membership_points_norma = {'a': s_values[0], 'b': s_values[1], 'c': s_values[2], 'd': s_values[3]}

        membership_values_y = self.graph_calculator.trapezoidalFunction(membership_points_y, wav_range)
        membership_values_transmission = self.graph_calculator.trapezoidalFunction(membership_points_transmission,
                                                                                   wav_range)
        membership_values_norma = self.graph_calculator.trapezoidalFunction(membership_points_norma, wav_range)

        ax.plot(wav_range * 1e6, membership_values_y, label='y(λ, T)')
        ax.plot(wav_range * 1e6, membership_values_transmission, label='τ(λ)')
        ax.plot(wav_range * 1e6, membership_values_norma, label='s(λ)')

        ax.fill_between(wav_range * 1e6, np.minimum(membership_values_y, membership_values_transmission), color='gray',
                        alpha=0.3)
        ax.fill_between(wav_range * 1e6, np.minimum(membership_values_y, membership_values_norma), color='black',
                        alpha=0.3)
        ax.fill_between(wav_range * 1e6, np.minimum(membership_values_y, np.minimum(membership_values_transmission,
                                                                                    membership_values_norma)),
                        color='gray', alpha=0.3)

        ax.set_xlabel('λ')
        ax.set_ylabel('')
        ax.set_title('Трапециевидная функция принадлежности')
        ax.grid(True)
        ax.legend()







