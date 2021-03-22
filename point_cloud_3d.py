# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS plugin to integrate Point Clouds from LIDAR or Photogrammetry
        copyright            : (C) David Hernandez Lopez
        email                : david.hernandez@uclm.es
 ***************************************************************************/
"""

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QDockWidget
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .point_cloud_3d_dockwidget import PointCloud3DDockWidget
import os.path

import sys
# sys.path.append("C:\Program Files\JetBrains\PyCharm 2018.3.3\debug-eggs\pycharm-debug.egg") # dhl
# sys.path.append("C:\Program Files\JetBrains\PyCharm 2020.3\debug-eggs\pydevd-pycharm.egg") # dhl
# import pydevd

from PyQt5.QtWidgets import QMessageBox,QFileDialog,QTabWidget,QInputDialog,QLineEdit
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, QDir, QObject, QFile
from qgis.core import QgsApplication, QgsDataSourceUri
pluginsPath = QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path()
pluginPath = os.path.dirname(os.path.realpath(__file__))
pluginPath = os.path.join(pluginsPath, pluginPath)
libCppPath = os.path.join(pluginPath, 'libCpp')
existsPluginPath = QDir(libCppPath).exists()
sys.path.append(pluginPath)
sys.path.append(libCppPath)
os.environ["PATH"] += os.pathsep + libCppPath
from libCpp.libPyPointCloud3D import IPyPC3DProject
from . import PC3DDefinitions


class PointCloud3D:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # pydevd.settrace('localhost',port=54100,stdoutToServer=True,stderrToServer=True)

        self.path_plugin = pluginPath
        self.path_libCpp = libCppPath
        self.current_plugin_name = PC3DDefinitions.CONST_SETTINGS_PLUGIN_NAME

        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PointCloud3D_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Point Cloud 3D')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PointCloud3D')
        self.toolbar.setObjectName(u'PointCloud3D')

        #print "** INITIALIZING PointCloudTools"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PointCloud3D', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/point_cloud_3d/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Point Cloud 3D'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING PointCloud3D"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD PointCloudTools"

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Point Cloud 3D'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            egm08UncompressFileName = libCppPath + "/" + PC3DDefinitions.CONST_EGM08_25_FILE_NAME
            if not QFile.exists(egm08UncompressFileName):
                egm08compressFileName = libCppPath + "/" + PC3DDefinitions.CONST_EGM08_25_COMPRESS_FILE_NAME
                text = "Before launching the plugin\n"
                text = "\nyou must unzip the file:\n"
                text += egm08compressFileName
                text += "\nin the same path using 7-zip, https://www.7-zip.org/"
                text += "\n\nThe unzipped file could not be uploaded\ndue to limitations in the Github account "
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                # msgBox.setWindowTitle(self.windowTitle)
                msgBox.setText(text)
                msgBox.exec_()
                return
            pythonModulePath = self.path_libCpp
            self.iPyProject = IPyPC3DProject()
            self.iPyProject.setPythonModulePath(self.path_libCpp)
            ret = self.iPyProject.initialize()
            path_file_qsettings = self.path_plugin + '/' + PC3DDefinitions.CONST_SETTINGS_FILE_NAME
            self.settings = QSettings(path_file_qsettings, QSettings.IniFormat)

            self.pluginIsActive = True

            #print "** STARTING PointCloudTools"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                connectionFileName = None  #WithoutPath = None
                # modelManagementFileName = None

                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PointCloud3DDockWidget(self.iface,
                                                            self.path_plugin,
                                                            self.path_libCpp,
                                                            self.current_plugin_name,
                                                            self.settings,
                                                            self.iPyProject,
                                                            connectionFileName)
                                                            # modelManagementFileName)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # # show the dockwidget
            # # TODO: fix to allow choice of dock location
            # self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            # self.dockwidget.show()
            # show the dockwidget
            # TODO: fix to allow choice of dock location
            # self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
                        # self.dockwidget.show()

            # bfg
            layersPanel = [x for x in self.iface.mainWindow().findChildren(QDockWidget) if x.objectName() == 'Layers']
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, layersPanel[0])
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.iface.mainWindow().tabifyDockWidget(layersPanel[0], self.dockwidget)
            self.iface.mainWindow().showNormal()
            self.iface.mainWindow().showMaximized()
            self.iface.mainWindow().update()

    def runFromAnotherPlugin(self,
                             iface,
                             path_plugin,
                             path_libCpp,
                             plugin_name,
                             iPyProject,
                             connectionFileName):
                             # modelManagementFileName):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.current_plugin_name = plugin_name
            # self.iPyProject = IPyPCTProject()
            # self.iPyProject.setPythonModulePath(self.path_libCpp)
            # ret = self.iPyProject.initialize()
            path_file_qsettings = self.path_plugin + '/' + PC3DDefinitions.CONST_SETTINGS_FILE_NAME
            self.settings = QSettings(path_file_qsettings, QSettings.IniFormat)

            self.pluginIsActive = True

            #print "** STARTING PointCloudTools"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PointCloud3DDockWidget(self.iface,
                                                            self.path_plugin,
                                                            self.path_libCpp,
                                                            self.current_plugin_name,
                                                            self.settings,
                                                            iPyProject,
                                                            connectionFileName)
                                                            # modelManagementFileName)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
