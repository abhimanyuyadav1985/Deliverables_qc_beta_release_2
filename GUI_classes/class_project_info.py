from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels, create_left_blank, create_center_data
from database_engine.DB_ops import fetch_project_info

class project_info(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):

        super(project_info, self).__init__(parent=parent)
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj  # use this line to pass the connection object between the parent and the child
        self.project_info = fetch_project_info(self.db_connection_obj)
        grid = QtGui.QGridLayout()
        grid.addWidget(create_central_labels('General Project information'), 0, 0, 1, 2)
        if self.project_info == None or len(self.project_info) == 0:
            grid.addWidget(create_center_data("Project information from ORCA is not available !!!"),1,0,1,2)
        else:
            info_dict = self.project_info[0].__dict__
            j = 0

            for key in info_dict:
                if key != '_sa_instance_state':
                    j= j+1
                    #print key , info_dict[key]
                    grid.addWidget(create_center_data(key),j,0)
                    grid.addWidget(create_left_blank(str(info_dict[key]),'blue'),j,1)

        self.setLayout(grid)




