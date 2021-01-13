# -*- coding: utf-8 -*-

# Import the PyQt and QGIS libraries
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5 import QtCore,uic
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QDialog,QTableWidgetItem,QListWidgetItem,QFileDialog,QMessageBox

# codificación utf-8
import os
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'process_list_edition_dialog.ui'))

#import GUI
#from ui_nombre_clase_dlg import Ui_nombreClaseDlg

#others imports
#from ..classes.Database import *

class ProcessListEditonDialog(QDialog, FORM_CLASS):
    """
    Brief:
    """

    def __init__(self,
                 title,
                 processList,
                 parent=None):
        """
        Brief:
        """
        super(ProcessListEditonDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)

        #self.lst_nombre_clase = lst_nombre_clase # contenedor lista para almacenar parámetros tras salvar valores introducidos en el panel

        self.title = title
        self.processList = processList

        # Set up the user interface from Designer.
        #self.ui = Ui_nombreClase()
        #self.ui.setupUi(self)

        # SIGNAL/SLOT connections in order:
        self.upPushButton.clicked.connect(self.upProcess)
        self.downPushButton.clicked.connect(self.downProcess)
        self.removePushButton.clicked.connect(self.removeSelectedProcesses)
        self.acceptItPushButton.clicked.connect(self.selectAcceptIt)

        self.initialize()

    def upProcess(self):
        numberOfSelectedRows = 0
        selectedRowPos = -1
        pos = -1
        for row in range(self.tableWidget.rowCount()):
            pos = pos + 1
            item = self.tableWidget.item(row,0)
            if item.isSelected():
                numberOfSelectedRows = numberOfSelectedRows + 1
                if numberOfSelectedRows > 1:
                    selectedRowPos = -1
                    break
                selectedRowPos = pos
        if selectedRowPos == -1:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(self.title)
            msgBox.setText("Select one row")
            msgBox.exec_()
            return
        return

    def downProcess(self):
        numberOfSelectedRows = 0
        selectedRowPos = -1
        pos = -1
        for row in range(self.tableWidget.rowCount()):
            pos = pos + 1
            item = self.tableWidget.item(row,0)
            if item.isSelected():
                numberOfSelectedRows = numberOfSelectedRows + 1
                if numberOfSelectedRows > 1:
                    selectedRowPos = -1
                    break
                selectedRowPos = pos
        if selectedRowPos == -1:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle(self.title)
            msgBox.setText("Select one row")
            msgBox.exec_()
            return
        return

    def removeSelectedProcesses(self):
        remove = False
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row,0)
            if item.isSelected():
                self.processList.remove(item.text())
                if not remove:
                    remove = True
        if remove:
            self.fillTabWidget()

    def fillTabWidget(self):
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)
        i = -1
        for procces in self.processList:
            itemName = QTableWidgetItem(procces)
            itemName.setTextAlignment(Qt.AlignHCenter)
            # itemName.setFlags(Qt.ItemIsSelectable)
            itemName.setBackground(QBrush(QColor(Qt.white),Qt.SolidPattern))
            itemName.setForeground(QBrush(QColor(Qt.black),Qt.SolidPattern))
            i = i + 1
            self.tableWidget.insertRow(i)
            self.tableWidget.setItem(i, 0, itemName)
        self.tableWidget.resizeColumnToContents(0)

    def getProcessList(self):
        return self.processList

    def initialize(self):
        if len(self.processList) > 0:
            self.fillTabWidget()

    def selectAcceptIt(self):
        self.accept()

