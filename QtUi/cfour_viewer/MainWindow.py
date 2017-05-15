# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 171, 151))
        self.groupBox.setObjectName("groupBox")
        self.keywordsButton = QtWidgets.QPushButton(self.groupBox)
        self.keywordsButton.setGeometry(QtCore.QRect(10, 110, 151, 32))
        self.keywordsButton.setObjectName("keywordsButton")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(10, 30, 151, 26))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.workstationtypeBox = QtWidgets.QComboBox(self.groupBox)
        self.workstationtypeBox.setGeometry(QtCore.QRect(10, 70, 151, 26))
        self.workstationtypeBox.setObjectName("workstationtypeBox")
        self.workstationtypeBox.addItem("")
        self.workstationtypeBox.addItem("")
        self.zmatpreviewBrowser = QtWidgets.QTextBrowser(self.centralWidget)
        self.zmatpreviewBrowser.setGeometry(QtCore.QRect(510, 40, 256, 192))
        self.zmatpreviewBrowser.setObjectName("zmatpreviewBrowser")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Calculation Parameters"))
        self.keywordsButton.setText(_translate("MainWindow", "Keywords"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Electronic Energy"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Properties"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Geometry Optimisation"))
        self.comboBox.setItemText(3, _translate("MainWindow", "Harmonic Frequencies"))
        self.workstationtypeBox.setItemText(0, _translate("MainWindow", "Local"))
        self.workstationtypeBox.setItemText(1, _translate("MainWindow", "Workstation"))

