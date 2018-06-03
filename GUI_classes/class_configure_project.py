# Created by Abhimanyu Yadav
# -------------------------- use ----------------------------------
# 1. create the GUI for the project configuration window
# class configuration_window()
#       def configure project
#       def is_ok_to_save
#       def save_list
#       def load_list
#       def use_configandquit
#       def check_path_DUG
#       def check_DB_connection
#       def check_DUG_connection
#------------------------------------------------------------------------

import sys, os
import paramiko
import pickle
from configuration.Tool_tips import tool_tips_mapper_dict
from PyQt4 import QtGui, QtCore
from configuration import *
from database_engine import DB_ops
from dug_ops import DUG_ops

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

def create_central_labels(label_text):
    labels_widget = QtGui.QLabel(label_text)
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setStyleSheet('background-color: rgb(65,65,65);color: white')
    return labels_widget

class save_project_configuration(): # This is used to create the object for the project configuration which is going to be saved as a pickle object

    def __init__(self, obj):
        #print"Initialzing the new pickle object from user inputs......"
        self.use_env = str(obj.use_env.currentText())
        ### Connection settings to access the database_engine host###
        self.host_IP = str(obj.host_IP.text())
        self.host_user = str(obj.host_user.text())
        self.host_pword = str(obj.host_pword.text())
        ## connection setting for the database_engine
        self.db_name = str(obj.db_name.text())
        self.db_user = str(obj.db_user.text())
        self.db_port = str(obj.db_port.text())
        self.db_pword = str(obj.db_pword.text())
        ### Connection settings to the DUG workstation
        self.DUG_IP = str(obj.DUG_IP.text())
        self.DUG_user = str(obj.DUG_user.text())
        self.DUG_pword = str(obj.DUG_pword.text())
        ## path to the files directories on DUG system
        self.DUG_segy_path = str(obj.DUG_segy_path.text()) # now we are refering to a single path for the parent directory for the DUG project
        #######################################

        #print "Pickle object initialization finished, now saving to file......."

class configuration_window(QtGui.QScrollArea): #The class object to create the configutation window GUI

    closed = QtCore.pyqtSignal()

    def __init__(self,  parent ):
        # define the top window
        super(configuration_window, self).__init__(parent)
        self.tool_tip_dict = tool_tips_mapper_dict['configuration']
        self.setToolTip(self.tool_tip_dict['configuration'])
        self.parent = parent
        # connection to the host for IRDB
        self.host_IP = []
        self.host_user = []
        self.host_pword = []
        # connection to database_engine
        self.db_name = []
        self.db_user = []
        self.db_port = []
        self.db_pword = []
        ### Connection settings to the DUG workstation
        self.DUG_IP = []
        self.DUG_user = []
        self.DUG_pword = []
        self.db_conn = []
        self.db_curr = []
        self.load_path = []
        self.configuration_status = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.configure_project()
        self.save_status = 0

    def configure_project(self):

        #print 'You are in Project configuration window...........'
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        # Titles for various widgets to be added to the grid

        title_host_IP = QtGui.QLabel('Database host IP ')
        title_host_user = QtGui.QLabel('Database host user')
        title_host_pword = QtGui.QLabel('Database host password')

        title_db_name = QtGui.QLabel('Database Name')
        title_db_user = QtGui.QLabel('Database user name')
        title_db_port = QtGui.QLabel('Database port')
        title_db_pword = QtGui.QLabel('Database password')

        title_DUG_IP = QtGui.QLabel('DUG WS IP')
        title_DUG_IP.setStyleSheet('color:blue')
        title_DUG_user = QtGui.QLabel("DUG user")
        title_DUG_user.setStyleSheet('color:blue')
        title_DUG_pword = QtGui.QLabel("DUG password")
        title_DUG_pword.setStyleSheet('color:blue')

        title_DUG_SEGY_parent_path = QtGui.QLabel('DUG project path')
        title_DUG_SEGY_parent_path.setStyleSheet('color: green')



        # Various widgets to be added to the grid
        self.host_IP = QtGui.QLineEdit()
        self.host_user = QtGui.QLineEdit()
        self.host_pword = QtGui.QLineEdit()
        ## connection setting for the database_engine
        self.db_name = QtGui.QLineEdit()
        self.db_user = QtGui.QLineEdit()
        self.db_port = QtGui.QLineEdit()
        self.db_pword = QtGui.QLineEdit()
        ### Connection settings to the DUG workstation
        self.DUG_IP = QtGui.QLineEdit()
        self.DUG_user = QtGui.QLineEdit()
        self.DUG_pword = QtGui.QLineEdit()
        ## path to the files directories on DUG system
        self.DUG_segy_path = QtGui.QLineEdit()


        #push button and their functions

        self.pushbutton_save = QtGui.QPushButton()
        self.pushbutton_save.setObjectName("Save config")
        self.pushbutton_save.setText("Save config")
        self.pushbutton_save.setStyleSheet("background-color: red")

        self.pushbutton_load = QtGui.QPushButton()
        self.pushbutton_load.setObjectName("Load config")
        self.pushbutton_load.setText("Load config")

        self.pushbutton_chk_db = QtGui.QPushButton()
        self.pushbutton_chk_db.setObjectName("Check DB connection")
        self.pushbutton_chk_db.setText("Check DB connection")
        self.pushbutton_chk_db.setStyleSheet("background-color: red")

        self.pushbutton_chk_DUG = QtGui.QPushButton()
        self.pushbutton_chk_DUG.setObjectName("Check DUG connection")
        self.pushbutton_chk_DUG.setText("Check DUG connection")
        self.pushbutton_chk_DUG.setStyleSheet("background-color: red")

        self.pushbutton_chk_DUG_path = QtGui.QPushButton()
        self.pushbutton_chk_DUG_path.setObjectName("Check path")
        self.pushbutton_chk_DUG_path.setText("Check DUG path")
        self.pushbutton_chk_DUG_path.setStyleSheet("background-color: red")


        self.pushbutton_commit = QtGui.QPushButton()
        self.pushbutton_commit.setObjectName("Use current config and continue")
        self.pushbutton_commit.setText("Use current cinfig and continue")
        self.pushbutton_commit.setStyleSheet("background-color: red")


        self.connect(self.pushbutton_save, QtCore.SIGNAL("clicked()"), self.save_list)
        self.connect(self.pushbutton_load, QtCore.SIGNAL("clicked()"), self.load_list_browse)

        self.connect(self.pushbutton_chk_db,QtCore.SIGNAL("clicked()"),self.check_DB_connection)

        self.connect(self.pushbutton_chk_DUG, QtCore.SIGNAL("clicked()"), self.check_DUG_connection)

        self.connect(self.pushbutton_chk_DUG_path,QtCore.SIGNAL("clicked()"),self.check_path_DUG)


        self.connect(self.pushbutton_commit, QtCore.SIGNAL("clicked()"), self.use_config_and_quit)


        # adding items to the grid
        title = create_central_labels("Configuration setup")
        title.setFixedHeight(20)
        grid.addWidget(title,0,0,1,3)
        grid.addWidget(title_host_IP,2,0)
        grid.addWidget(title_host_user,3,0)
        grid.addWidget(title_host_pword,4,0)

        grid.addWidget(title_db_name,5,0)
        grid.addWidget(title_db_user,6,0)
        grid.addWidget(title_db_port, 7, 0)
        grid.addWidget(title_db_pword, 8, 0)

        grid.addWidget(title_DUG_IP, 9, 0)
        grid.addWidget(title_DUG_user, 10, 0)
        grid.addWidget(title_DUG_pword, 11, 0)


        grid.addWidget(title_DUG_SEGY_parent_path,12,0)


        grid.addWidget(self.host_IP,2, 1)
        grid.addWidget(self.host_user, 3, 1)
        grid.addWidget(self.host_pword, 4, 1)

        grid.addWidget(self.db_name, 5, 1)
        grid.addWidget(self.db_user, 6, 1)
        grid.addWidget(self.db_port, 7, 1)
        grid.addWidget(self.db_pword, 8, 1)

        grid.addWidget(self.DUG_IP, 9, 1)
        grid.addWidget(self.DUG_user, 10, 1)
        grid.addWidget(self.DUG_pword, 11, 1)


        grid.addWidget(self.DUG_segy_path, 12, 1)



        grid.addWidget(self.pushbutton_save,18,0)
        grid.addWidget(self.pushbutton_load,17,0)
        self.load_path = QtGui.QLineEdit()
        grid.addWidget(self.load_path,17,1)
        grid.addWidget(self.pushbutton_commit,18,1)

        grid.addWidget(self.pushbutton_chk_db,8,2)
        grid.addWidget(self.pushbutton_chk_DUG, 11, 2)
        grid.addWidget(self.pushbutton_chk_DUG_path, 12, 2)


        self.setWindowTitle("Project configutation")
        self.setWindowIcon(QtGui.QIcon('polarcus.png'))  # change thi sin the future
        self.setGeometry(100, 100, 1000, 1000)

        grid.addWidget(QtGui.QLabel('Vessel'),1,0)
        use_env = QtGui.QComboBox()
        use_env.addItems(use_locations)
        self.use_env = use_env
        grid.addWidget(self.use_env,1,1)
        self.setLayout(grid)



    def is_ok_to_save(self):
        self.save_status = 0
        for i in range(11):
            self.save_status += int(self.configuration_status[i])
        if self.save_status ==11:
            self.pushbutton_save.setStyleSheet("background-color: green")

    def save_list(self):
        self.configuration_status = [0,0,0,0,0,0,0,0,0,0,0]


        self.pushbutton_chk_DUG_path.setStyleSheet("background-color: red")


        self.pushbutton_chk_db.setStyleSheet("background-color: red")
        self.pushbutton_chk_DUG.setStyleSheet("background-color: red")

        self.check_DB_connection()
        self.check_DUG_connection()

        self.check_path_DUG()


        sumstatus = 0

        for i in range(11):
            sumstatus += int(self.configuration_status[i])
        if sumstatus ==11:
            #print "Saving the project configuration to configuration.ini"
            logger.info( "Saving the project configuration to configuration.ini")
            config_obj = save_project_configuration(self)
            status_existing_config = os.path.exists(os.path.join(os.getcwd(), "Tape_QC_configuration.ini"))
            if status_existing_config:
                #print "Deleting the old configuration file......"
                os.remove(os.path.join(os.getcwd(), "Tape_QC_configuration.ini"))
            file_name = os.path.join(os.getcwd(), conn_config_file)
            #print "Creating the new configuration file %s", file_name
            logger.info("Creating the new configuration file")
            filehandler = open(file_name, "wb")
            pickle.dump(config_obj, filehandler)
            filehandler.close()
            #print "New configuration file saved , you can now use it..."
            logger.info("New configuration file saved , you can now use it...")
            self.pushbutton_commit.setStyleSheet("background-color: green")
            self.save_status = 1
            #DUG_ops.transfer_SEGY_check_script()
        else:
            #print "Unable to save, Some of the configuraitons may be empty or incorrect ..."
            logger.info("Unable to save, Some of the configuraitons may be empty or incorrect ...")

    def load_list(self):
        status = os.path.exists(str(self.load_path.text()))
        if status:
            #print "File found, now loading..." + str(self.load_path.text())
            logger.info(str("File found, now loading..." + str(self.load_path.text())))

            file_handler = open(str(self.load_path.text()),'rb')
            config_obj = pickle.load(file_handler)
            file_handler.close()
            self.host_IP.setText(str(config_obj.host_IP))
            self.host_user.setText(str(config_obj.host_user))
            self.host_pword.setText(str(config_obj.host_pword))

            self.db_name.setText(str(config_obj.db_name))
            self.db_user.setText(str(config_obj.db_user))
            self.db_port.setText(str(config_obj.db_port))
            self.db_pword.setText(str(config_obj.db_pword))

            self.DUG_IP.setText(str(config_obj.DUG_IP))
            self.DUG_user.setText(str(config_obj.DUG_user))
            self.DUG_pword.setText(str(config_obj.DUG_pword))

            self.DUG_segy_path.setText(str(config_obj.DUG_segy_path))

            self.check_DB_connection()
            self.check_DUG_connection()
            self.check_path_DUG()


        else:
           logger.info("Sorry the specified file does not exist .....")

    def load_list_browse(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
        self.load_path.setText(fname)
        self.show()
        #print "Checking if the selected File exists..."
        status = os.path.exists(fname)
        if status:
            logger.info("File found, now loading..." + str(self.load_path.text()))
            file_handler = open(fname, 'rb')
            config_obj = pickle.load(file_handler)
            file_handler.close()
            index = self.use_env.findText(str(config_obj.use_env), QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.use_env.setCurrentIndex(index)
            self.host_IP.setText(str(config_obj.host_IP))
            self.host_user.setText(str(config_obj.host_user))
            self.host_pword.setText(str(config_obj.host_pword))

            self.db_name.setText(str(config_obj.db_name))
            self.db_user.setText(str(config_obj.db_user))
            self.db_port.setText(str(config_obj.db_port))
            self.db_pword.setText(str(config_obj.db_pword))

            self.DUG_IP.setText(str(config_obj.DUG_IP))
            self.DUG_user.setText(str(config_obj.DUG_user))
            self.DUG_pword.setText(str(config_obj.DUG_pword))

            self.DUG_segy_path.setText(str(config_obj.DUG_segy_path))

            #print "All the congirations are loaded, now checking for validitiy...."
            self.check_DB_connection()
            self.check_DUG_connection()
            self.check_path_DUG()

        else:
            logger.warning("Sorry the specified file does not exist .....")

    def use_config_and_quit(self):
        if self.save_status == 1:
            logger.info("For the current session using the saved configuration")
            self.close()
        else:
            logger.warning("No valid configuration_available.....")

    def check_path_DUG(self):
        logger.info("Checking the path for DUG project.........")
        #print "Checking the path for DUG project........."
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(str(self.DUG_IP.text()), username=str(self.DUG_user.text()), password=str(self.DUG_pword.text()))
        cmd = "python " + '/d/home/share/bin/directory_checking_script.py ' + str(self.DUG_segy_path.text())
        #print cmd
        stdin, stdout, stderr = client.exec_command(cmd)
        outlines = stdout.readlines()
        status = outlines[0].rstrip()
        #print status
        client.close()
        if status == "True":
            self.pushbutton_chk_DUG_path.setStyleSheet("background-color: green")
            #print "Found the path for DUG project:: " + str(self.DUG_segy_path.text())
            logger.info(str("Found the path for DUG project:: " + str(self.DUG_segy_path.text())))
            self.configuration_status[10] = 1
            self.is_ok_to_save()
        else:
            #print "The specified path does not exist..."
            logger.error("The specified path does not exist...")


    def check_DUG_connection(self):
        host = str(self.DUG_IP.text())
        port = 22
        username = str(self.DUG_user.text())
        password = str(self.DUG_pword.text())
        #print "The DUG connection setting are:::" + str(host) + " " + str(username) + "  " + str(password)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, username=username, password=password)
            if client.get_transport().is_active():
            #print "Connection to DUG workstation sucessful!!!!!"
                logger.info("Connection to DUG workstation sucessful.....")
                self.pushbutton_chk_DUG.setStyleSheet("background-color: green")
                transport = paramiko.Transport((host, port))
                transport.connect(username=username, password=password)
                sftp_client = paramiko.SFTPClient.from_transport(transport)
                DUG_ops.transfer_directory_checking_script(sftp_client)
                for i in range(7,10):
                    self.configuration_status[i] = 1
                    self.is_ok_to_save()
        except Exception as error:
            logger.error(error)
            logger.error("Connection to DUG workstation unsucessful, exiting application!!!!!")
            sys.exit()


        #print "Please check settings to the DUG workstation"

    def check_DB_connection(self): #this function is used to check if the databse connection settings are correct
        #print "The user input for DB connection are:"
        #print str(self.host_IP.text()), str(self.host_user.text()), str(self.host_pword.text()), str(self.db_name.text()), str(self.db_user.text()),str(self.db_port.text()),str(self.db_pword.text())
        try:
            DB_ops.test_db_connection_for_config(self)
            self.pushbutton_chk_db.setStyleSheet("background-color: green")
            for i in range(7):
                self.configuration_status[i] = 1
                self.is_ok_to_save()
        except Exception as error:
            #print "The databse settings are incorrect......"
            logger.error("The databse settings are incorrect......now exiting")
            logger.error(error)
            sys.exit()




    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
