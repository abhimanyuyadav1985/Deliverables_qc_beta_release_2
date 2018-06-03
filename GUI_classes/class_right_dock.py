from PyQt4 import QtGui, QtCore
from general_functions.general_functions import *
from database_engine.DB_ops import *
from configuration import *
import os
#----------class_imports -----

#-----------------------------

class right_widget(QtGui.QScrollArea):

    config_status_signal = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        # define the top window
        self.parent = parent
        super(right_widget, self).__init__(parent=parent)

        self.parent.config_status_signal.connect(self.config_status)
        self.config_status_signal.connect(self.fetch_config_details)

        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(create_central_labels("Config Status"),0,0)


    def config_status(self,status_bool):
        if status_bool ==True:
            self.grid.addWidget(create_true_label(),1,0)
            self.config_status_signal.emit(True)
        else:
            self.grid.addWidget(create_false_label(), 1, 0)
            self.config_status_signal.emit(False)
        self.setLayout(self.grid)

    def fetch_config_details(self,status_bool):
        line_edit_w = []
        file_path = os.path.join(os.getcwd(), conn_config_file)
        if os.path.exists(file_path):
            config_details = fetch_config_info()
        else:
            pass
        self.grid.addWidget(create_central_labels('Database IP'),2,0)
        self.grid.addWidget(create_central_labels('Database User'), 4, 0)
        self.grid.addWidget(create_central_labels('Database Name'), 6, 0)
        self.grid.addWidget(create_central_labels('DUG IP'), 8, 0)
        self.grid.addWidget(create_central_labels('DUG User'), 10, 0)
        self.grid.addWidget(create_central_labels('DUG Project path'), 12, 0)
        self.grid.addWidget(create_central_labels('SW use Mode'), 14, 0)
        mode_use = QtGui.QLabel()
        if self.parent.default_use_mode is False:
            mode_use.setText('Development')
        else:
            mode_use.setText('Production')
        self.grid.addWidget(mode_use,15,0)
        self.grid.addWidget(create_central_labels('Sw use environment'), 16, 0)
        prod_env = QtGui.QLabel()
        prod_env.setText(self.parent.default_use_env)
        self.grid.addWidget(prod_env, 17, 0)

        for i in range(3,15,2):
            line_edit_w.append(QtGui.QLabel())
            self.grid.addWidget(line_edit_w[((i-1)/2)-1],i,0)
        if status_bool == True:
            for i in range (0,len(line_edit_w)):
                line_edit_w[i].setText(config_details[i])
