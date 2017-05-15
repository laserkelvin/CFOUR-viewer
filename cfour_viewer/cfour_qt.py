import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QAction, qApp, QMainWindow,
QDesktopWidget, QVBoxLayout, QComboBox, QGroupBox, QGridLayout)
#from PyQt5.QtGui import *

def startQt():
    """ This function should be called to start the QtViewer. """
    app = QApplication(sys.argv)
    MainInstance = MainWindow()
    sys.exit(app.exec_())

calc_methods = [
    "Electronic Energy",
    "Optimisation",
    "Properties",
    "Harmonic Frequencies"
]

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow).__init__()
        self.initUI()

    def initUI(self, parent=None):
        self.resize(800, 600)
        self.center()                          # call centering method
        self.setWindowTitle("CFOUR Viewer")

        # Add a status bar, and initialise message
        self.statusBar().showMessage("Ready.")

        layout = QGridLayout()
        self.setLayout(layout)

        # Initialise toolbar
        # self.toolbar = self.addToolBar("Exit")
        # self.toolbar.addAction(exitToolbarInit())   # method defined below

        self.calctypes_combo = self.generate_combobox(calc_methods)
        layout.addWidget(self.calctypes_combo)

        # Initialise calculation parameters vbox
        # self.parameters_layout()
        self.show()

    def center(self):
        """ Centers the window """
        qr = self.frameGeometry()
        # This figures out the resolution of the screen and gets the center
        cp = QDesktopWidget().availableGeometry().center()
        # Move window to the center defined by resolution of the screen
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def generate_combobox(self, items, size=[150, 400]):
        combobox = QComboBox()
        for item in items:
            combobox.addItem(item)
        combobox.setMinimumWidth(size[0])
        combobox.setMaximumWidth(size[1])
        return combobox

    def generate_groupbox(self, name, widgets, boxlayout):
        groupbox = QGroupBox(name)
        groupbox.setCheckable(True)
        layout = boxlayout
        groupbox.setLayout(layout)
        for widget in widgets:
            groupbox.addWidget(widget)
        return groupbox

if __name__ == "__main__":
    startQt()
