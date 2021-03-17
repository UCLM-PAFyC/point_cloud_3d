# -*- coding: utf-8 -*-
# Import PyQt5 classes
from PyQt5 import uic
from PyQt5 import QtWidgets

# Import Python classes
import os

import sys
sys.path.append(os.path.dirname(__file__))
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),
                                            'point_cloud_3d_about_qdialog.ui'),
                               resource_suffix='')

class AboutQDialog(QtWidgets.QDialog,
                         FORM_CLASS):
    def __init__(self,
                 parent=None):
        """Constructor."""
        super(AboutQDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)