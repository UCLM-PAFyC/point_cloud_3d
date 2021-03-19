# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS plugin to integrate Point Clouds from LIDAR or Photogrammetry
        copyright            : (C) David Hernandez Lopez
        email                : david.hernandez@uclm.es
 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PyQt5 import QtCore,uic
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QDialog,QTableWidgetItem,QListWidgetItem,QFileDialog

from qgis.core import *
from qgis.gui import QgsMessageBar

# codificación utf-8
import os
import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'multiple_file_selector_dialog.ui'))

#import GUI
#from ui_nombre_clase_dlg import Ui_nombreClaseDlg

#others imports
#from ..classes.Database import *

class MultipleFileSelectorDialog(QDialog, FORM_CLASS):
    """
    Brief:
    """

    def __init__(self,
                 iface,
                 path,
                 title,
                 fileTypes,
                 files,
                 activeFileExtensions,
                 parent=None):
        """
        Brief:
        """
        super(MultipleFileSelectorDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)

        #self.lst_nombre_clase = lst_nombre_clase # contenedor lista para almacenar parámetros tras salvar valores introducidos en el panel

        self.iface = iface # Save reference to the QGIS interface
        self.path = path
        self.title = title
        self.fileTypes = fileTypes
        self.files = files
        self.activeFileExtensions = activeFileExtensions

        # Set up the user interface from Designer.
        #self.ui = Ui_nombreClase()
        #self.ui.setupUi(self)

        # SIGNAL/SLOT connections in order:
        self.pushButton_selectFiles.clicked.connect(self.selectFiles)
        self.pushButton_selectDirectory.clicked.connect(self.selectDirectory)
        self.pushButton_selectDirectories.clicked.connect(self.selectDirectories)
        self.pushButton_deleteSelectedFiles.clicked.connect(self.deleteSelectedFiles)
        self.acceptItPushButton.clicked.connect(self.selectAcceptIt)

        self.initialize()

    def addFilesFromDirectory(self,dir, addFromSubDir):
        fileInfoList=dir.entryInfoList()
        insertFile = False
        for fileInfo in fileInfoList:
            if fileInfo.isFile():
                fileName = fileInfo.absoluteFilePath()
                if fileName in self.files:
                    continue
                fileExtension = fileInfo.suffix().lower()
                if not fileExtension in self.activeFileExtensions:
                    continue
                filePath = fileInfo.absolutePath()
                self.path = filePath
                self.files.append(fileName)
                if not insertFile:
                    insertFile = True
            if fileInfo.isDir() and addFromSubDir:
                if fileInfo.baseName(): # para quitar el . y el ..
                    subDir = QDir(fileInfo.absoluteFilePath())
                    insertFileFromSubDir = self.addFilesFromDirectory(subDir,addFromSubDir)
                    if not insertFile and insertFileFromSubDir:
                        insertFile = True
        return insertFile

    def deleteSelectedFiles(self):
        removeFile = False
        for row in range(self.tableWidget_selectedFiles.rowCount()):
            item = self.tableWidget_selectedFiles.item(row,0)
            if item.isSelected():
                self.files.remove(item.text())
                if not removeFile:
                    removeFile = True
        if removeFile:
            self.fillTabWidget()

    def existsFileTypesChecked(self):
        existsFileTypesChecked = False
        self.activeFileExtensions = []
        for j in range(self.listWidget_fileTypes.count()):
            item = self.listWidget_fileTypes.item(j)
            if item.checkState():
                if not existsFileTypesChecked:
                    existsFileTypesChecked = True
                self.activeFileExtensions.append(item.text())
        return existsFileTypesChecked

    def fillTabWidget(self):
        for i in range(self.tableWidget_selectedFiles.rowCount()):
            self.tableWidget_selectedFiles.removeRow(0)
        i = -1
        for fileName in self.files:
            itemFileName = QTableWidgetItem(fileName)
            itemFileName.setTextAlignment(Qt.AlignHCenter)
            itemFileName.setFlags(Qt.ItemIsSelectable)
            itemFileName.setBackground(QBrush(QColor(Qt.white),Qt.SolidPattern))
            itemFileName.setForeground(QBrush(QColor(Qt.black),Qt.SolidPattern))
            i = i + 1
            self.tableWidget_selectedFiles.insertRow(i)
            self.tableWidget_selectedFiles.setItem(i, 0, itemFileName)
        self.tableWidget_selectedFiles.resizeColumnToContents(0)

    def getActiveFileExtensions(self):
        return self.activeFileExtensions

    def getFiles(self):
        return self.files

    def getPath(self):
        return self.path

    def initialize(self):
        for i in range(len(self.fileTypes)):
            type = self.fileTypes[i]
            item = QListWidgetItem(type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if type in self.activeFileExtensions:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.listWidget_fileTypes.insertItem(i,item)
        if len(self.files) > 0:
            self.fillTabWidget()

    def selectAcceptIt(self):
        self.accept()

    def selectFiles(self):
        if not self.existsFileTypesChecked():
            self.iface.messageBar().pushMessage(self.title,
                                                    "Before select files you must check some file type",
                                                    QgsMessageBar.CRITICAL,
                                                    10)
            return
        filters="Ficheros ("
        for j in range(self.listWidget_fileTypes.count()):
            item = self.listWidget_fileTypes.item(j)
            if item.checkState():
                filters = filters + "*." + item.text() + " "
        filters = filters + ")"
        filesNames, _ = QFileDialog.getOpenFileNames(self,self.title,self.path,filters)
        insertFile = False
        for fileName in filesNames:
            fileInfo = QFileInfo(fileName) # por las barras
            fileName = fileInfo.absoluteFilePath()
            if fileName in self.files:
                continue
            fileExtension = fileInfo.suffix().lower()
            if fileExtension in self.activeFileExtensions:
                filePath = fileInfo.absolutePath()
                self.path = filePath
                self.files.append(fileName)
                if not insertFile:
                    insertFile = True
        if insertFile:
            self.fillTabWidget()

    def selectDirectory(self):
        if not self.existsFileTypesChecked():
            self.iface.messageBar().pushMessage(self.title,
                                                    "Before select files you must check some file type",
                                                    QgsMessageBar.CRITICAL,
                                                    10)
            return
        strDir = QFileDialog.getExistingDirectory(self,"Select directory",self.path,
                                                  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if strDir:
            dir = QDir(strDir)
            if self.addFilesFromDirectory(dir,False):
                self.fillTabWidget()

    def selectDirectories(self):
        if not self.existsFileTypesChecked():
            self.iface.messageBar().pushMessage(self.title,
                                                    "Before select files you must check some file type",
                                                    QgsMessageBar.CRITICAL,
                                                    10)
            return
        strDir = QFileDialog.getExistingDirectory(self,"Select main directory",self.path,
                                                  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if strDir:
            dir = QDir(strDir)
            if self.addFilesFromDirectory(dir,True):
                self.fillTabWidget()