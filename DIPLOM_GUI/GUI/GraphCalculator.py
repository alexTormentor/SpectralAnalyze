from Modules import np


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