from Modules import np, math

# Constructor Pattern
class GraphCalculator:
    @staticmethod
    def y(lambda_val, T):
        c2 = (6.62607015e-34 * 2.99792458e8) / 3.3805e-23
        x = 4.9651 * ((lambda_val * T) / c2)
        exponent = np.exp(4.9651 / x)
        denominator = exponent - 1
        result = 142.32 * x ** -5 * denominator ** -1
        return result

    @staticmethod
    def planck_wien(wav, T):
        h = 6.62607015e-34
        c = 2.99792458e8
        k = 1.380649e-23
        b = h * c / (wav * k * T)
        intensity = (2.0 * h * c ** 2) / ((wav ** 5) * (np.exp(b) - 1.0))
        peak_wav = (2.897771955e-3) / T
        return intensity, peak_wav

    @staticmethod
    def spectral_density(lamda, Theta):
        '''
        Функция расчёта спектральной плотности энергетической светимости.

        Параметры:
        lamda (float): длина волны.
        Theta (float): значение температуры.

        Возвращаемое значение:
        M (float): распределение спектральной плотности.
        '''
        c1 = 2 * math.pi * 6.62607015e-34 * 2.99792458e8 ** 2
        c2 = (6.62607015e-34 * 2.99792458e8) / 3.3805e-23

        expon = np.exp(c2 / (lamda * Theta))
        denominator = expon - 1

        M = c1 * lamda ** -5 * denominator ** -1

        return M

    @staticmethod
    def trapezoidalFunction(points, xrange):
        values = []
        for x in xrange:
            if x <= points['a']:
                values.append(0)
            elif (x >= points['a'] and x <= points['b']):
                values.append((x - points['a']) / (points['b'] - points['a']))
            elif x >= points['b'] and x <= points['c']:
                values.append(1)
            elif (x >= points['c'] and x <= points['d']):
                values.append((points['d'] - x) / (points['d'] - points['c']))
            elif x >= points['d']:
                values.append(0)
        return values
