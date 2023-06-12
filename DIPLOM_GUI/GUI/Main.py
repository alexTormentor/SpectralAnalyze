from Modules import QtWidgets, sys
from Spectra import  Spectra

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = Spectra()
    window.show()
    sys.exit(app.exec_())
