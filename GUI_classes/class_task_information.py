from PyQt4 import QtGui
import os
import pickle
from general_functions.general_functions import create_central_labels
import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)


class running_task_log(QtGui.QWidget):
    def __init__(self, parent):
        super(running_task_log, self).__init__()
        self.parent = parent
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.active_task_file_path = os.path.join(os.getcwd(),'temp','active_tasks')
        self.setWindowTitle("Active Task information")

        if os.path.exists(self.active_task_file_path):
            self.extract_task_info()
            if bool(self.task_dict):
                self.add_info_widgets()
            else:
                logger.warning("No active tasks available")
                self.add_none()
        else:
            self.add_none()

    def add_none(self):
        message = "No active tasks"
        self.grid.addWidget(create_central_labels(message),0,0)

    def extract_task_info(self):
        file_handler = open(self.active_task_file_path,'rb')
        self.task_dict = pickle.load(file_handler)
        file_handler.close()

    def add_info_widgets(self):
        self.tabs = QtGui.QTabWidget()
        self.tabs.setMinimumWidth(1200)
        self.grid.addWidget(self.tabs,0,0,1,5)
        pb_refresh = QtGui.QPushButton('Refresh logs')
        pb_refresh.clicked.connect(self.refresh_logs)
        self.grid.addWidget(pb_refresh,1,4)
        self.tab_list = []
        for a_drive in self.task_dict.keys():
            self.tab_list.append(single_task_information(self,self.task_dict[a_drive][7]))
            self.tabs.addTab(single_task_information(self,self.task_dict[a_drive][7]))

    def refresh_logs(self):
        logger.warning("Tool will be available soon..")

class single_task_information(QtGui.QScrollArea):
    def __init__(self,parent,log_path):
        super(single_task_information, self).__init__()
        self.parent = parent
        self.setMinimumWidth(1200)
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.textbox = QtGui.QTextEdit()
        self.textbox.setStyleSheet('''
            QTextEdit {
                font: 10pt "Consolas";
            }
        ''')
        self.textbox.setMinimumWidth(1200)
        self.textbox.setMinimumHeight(800)
        self.log_path = log_path
        self.setWidget(self.textbox)
        self.update_info()


    def update_info(self):
        cmd = 'python /d/home/share/bin/run_log_fetcher.py ' + self.log_path
        stdin, stdout, stderr = self.DUG_connection_obj.ws_client.exec_command(cmd)
        encoded_text = stdout.read()
        decoded_text = encoded_text.decode('base64')
        for a_line in decoded_text.split("\n"):
            self.textbox.append(a_line.rstrip("\n"))






