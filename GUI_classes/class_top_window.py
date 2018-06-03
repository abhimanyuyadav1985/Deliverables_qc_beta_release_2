from configuration import *
#------------------------------------------------------------------
# Services
#-------------------------------------------------------------------
from Tape_services.class_tape_operation_manager import Tape_operation_manager
from database_engine.db_engine_setup import *
from dug_ops.DUG_connection import DUG_connection_object
from dug_ops.DUG_ops import transfer_SEGY_check_script,transfer_base_64_encoder,transfer_SEGD_QC_parser_script
from dug_ops.DUG_ops import check_generic_path,create_generic_directory, transfer_sgyt_encoder
from general_functions.class_synchronization_service import Synchronization_service
from dug_ops.DUG_ops import transfer_run_daemons, transfer_run_log_fetcher
from dug_ops.DUG_ops import run_command_on_tape_server
#-------------------------------------------------------------------
# Widgets
#-------------------------------------------------------------------
from class_configure_project import *
from class_deliverables_window import *
from class_left_dock import *
from class_project_info import project_info
from class_right_dock import *
from class_segd_tool_window import *
from class_single_deliverable import add_new_deliverable,view_single_deliverable_detail,edit_single_deliverable
from class_tape_drive_dashboard import Tape_drive_dashboard
from class_shipment_summary import shipment_summary
from class_single_shipment import add_new_shipment,edit_shipment
from class_SEGD_QC_summary import refresh_enabled_SEGD_QC_summary
from class_segy_tool_window import SEGY_Tool_Window
from class_shipments_window import shipment_tools
from class_usb_functions_window import usb_tools_window
from class_single_usb_window import add_usb_label,edit_usb_window
from class_USB_summary_window import usb_summary_window
from class_thread_dock import threads_dock
from class_SEGY_QC_status import SEGY_qc_status

#----------- general functions --------------------------------------
from general_functions.class_run_information_synchronization import run_information_sync
from general_functions.general_functions import create_central_labels
from database_engine.DB_ops import get_project_name
from general_functions.class_threads import Worker
from class_reporter.class_change_delete_log_report import change_log_report
import posixpath
#-----------------------------

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)



####################################################################################################################################
###Main window
####################################################################################################################################


class Top_Window(QtGui.QMainWindow):

    """

    Top_window is the main window for the application

    """

    closed = QtCore.pyqtSignal()
    config_status_signal = QtCore.pyqtSignal(bool)

    def __init__(self):

        """
        Initialization protocol =>


        :param log_file_path:
        """

        super(Top_Window, self).__init__()
        # Create the logging services 1st so that all the executions can be logged

        self.config_check = False
        self.tape_dashboard_visible = False
        self.layout = QtGui.QGridLayout()
        self.default_central_widget = QtGui.QWidget(self)
        self.default_central_widget.setLayout(self.layout)
        self.setCentralWidget(self.default_central_widget)
        self.statusBar()

        #------creating the top window------------

        self.add_threads()
        self.set_window_title_and_icon()
        self.set_default_use_env()
        self.set_dummy_central_widget()
        self.set_logo_and_title()
        self.add_left_dock()
        self.add_config_message()
        self.add_right_dock()
        self.add_run_log()
        self.set_connection_object()
        self.set_config_message()
        self.add_thread_dock()

        #-----------------------------------------

        self.show()

#-----------------------------------------------------------------------------+
    # Functions for Top window GUI
#------------------------------------------------------------------------------+


    
    
    def add_threads(self):

        """
        Adds four threads self.thread[1-4] and creates a self.thread_dict

        :return: none

        """

        self.thread1 = Worker("excel")
        self.thread2 = Worker("dug")
        self.thread3 = Worker("db")
        self.thread4 = Worker("general")

        self.thread_dict = {'excel':['thread1' , self.thread1], 'dug' : ['thread2' ,self.thread2], 'db' : ['thread3', self.thread3], 'general':['thread4', self.thread4]}

    
    
    def set_window_title_and_icon(self):
        """
        Add application version from configuration.__init__()

        Add polarcus logo from images in media

        :return: none
        """
        title = "Polarcus Tape QC V" + version
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(),media_path,'polarcus.png')))# change this in the future

    
    
    def set_default_use_env(self):
        """
        set use location and use mode from configuration

        :return: none
        """
        self.config_check = False
        self.default_use_mode = default_use_mode
        self.default_use_env = default_use_env

        logger.info("Default use mode: " + str(default_use_mode))
        logger.info("Default use environment: " + default_use_env )

    
    
    def set_dummy_central_widget(self):
        """
        Sets a dummy empty widget

        :return: none
        """
        plcs_logo = QtGui.QLabel()
        myPixmap = QtGui.QPixmap(os.path.join(os.getcwd(), media_path, 'deliverables_qc.png'))
        pixmap_resized = myPixmap.scaled(800, 800, QtCore.Qt.KeepAspectRatio)
        plcs_logo.setPixmap(pixmap_resized)
        self.working_widget = plcs_logo
        self.layout.addWidget(self.working_widget, 1, 1)

    
    
    def set_logo_and_title(self):
        """
        Add various widget titles and Polarcus logo to the application

        :return: none
        """
        plcs_logo = QtGui.QLabel()
        myPixmap = QtGui.QPixmap(os.path.join(os.getcwd(),media_path,'polarcus.png'))
        pixmap_resized = myPixmap.scaled(100, 50, QtCore.Qt.KeepAspectRatio)
        plcs_logo.setPixmap(pixmap_resized)
        plcs_logo.setFixedSize(100,50)
        self.layout.addWidget(plcs_logo,0,0)
        #Addition of window title
        ca_title = create_central_labels('Deliverables QC Application')
        ca_title.setStyleSheet('background-color: rgb(140,198,63);color: black')
        ca_title.setFont(QtGui.QFont('SansSerif', 20))
        self.layout.addWidget(ca_title,0,1)
        ############ ading label for status info
        sts_title = create_central_labels('Configuration')
        sts_title.setStyleSheet('background-color: rgb(65,65,65);color: white')
        sts_title.setFont(QtGui.QFont('SansSerif', 15))
        self.layout.addWidget(sts_title, 0, 2)
        # addind title for message board
        # runlog_title = create_central_labels('Run time Log')
        # runlog_title.setStyleSheet('background-color: rgb(65,65,65);color: white')
        # runlog_title.setFont(QtGui.QFont('SansSerif', 15))
        # self.layout.addWidget(runlog_title, 0, 3)
        # add thread dock
        thread_dock_title = create_central_labels('Thread status')
        thread_dock_title.setStyleSheet('background-color: rgb(65,65,65);color: white')
        thread_dock_title.setFont(QtGui.QFont('SansSerif', 15))
        self.layout.addWidget(thread_dock_title, 0, 3)

    
    
    def add_left_dock(self):
        """
        Adds the main menu from the class_left_dock.left_dock

        :return: None
        """
        #Addition of main menu
        self.cw = left_dock(self)
        self.cw.setMaximumHeight(500)
        self.cw.setFixedWidth(150)
        self.layout.addWidget(self.cw,1,0)

    
    
    def add_config_message(self):
        #Configuration message
        config_message_label = create_central_labels('Config Message:::')
        config_message_label.setMaximumHeight(30)
        #self.layout.addWidget(config_message_label,2,0,1,1)
        self.config_message = QtGui.QLineEdit()
        self.config_message.setMinimumWidth(600)
        #self.layout.addWidget(self.config_message,2,1,1,2)

    
    
    def add_right_dock(self):
        """
        Adds the configuration settings from class_righ_dock.right_widget

        :return: None
        """
        #Right status widget
        self.sts_inf = right_widget(self)
        self.sts_inf.setMaximumHeight(500)
        self.sts_inf.setFixedWidth(130)
        self.layout.addWidget(self.sts_inf,1,2)

    
    
    def add_thread_dock(self):
        self.thread_dock = threads_dock(self)
        self.thread_dock.setFixedWidth(220)
        self.layout.addWidget(self.thread_dock, 1, 3)


    def add_run_log(self):
        self.run_log = QtGui.QTextEdit()
        self.run_log.setFixedWidth(350)
        #self.layout.addWidget(self.run_log,1,3)

    def set_connection_object(self):
        self.connection_obj = None

    def set_config_message(self):
        #self.check_existing_config()
        logger.info("Configuration status is set to: " + str(self.config_check))
        logger.info("Either add a new configuration or use Refresh to load existing")
        if self.config_check is False:
            self.config_status_signal.emit(False)
        #Adddition of test functionality

        #time.sleep(2)

#---------------------------------------------------------------------------------+
#         Functions related to startup and services
#---------------------------------------------------------------------------------+

    
    def check_existing_config(self):
        config_window = configuration_window(self)
        if os.path.exists(os.path.join(os.getcwd(), conn_config_file)):
            logger.info("Found an existing configuration now checking its validitiy!!")
            config_window.load_path.setText(os.path.join(os.getcwd(), conn_config_file))
            config_window.load_list()
            if config_window.save_status == 11:
                #self.cw.btn3.setStyleSheet("background-color : green")
                logger.info(" Found a valid configuration, the applicaiton will use it. If you need to change use the configuration button....")
                self.config_check = True
                logger.info('config_check set to : True')
                self.verified_start_up_protocol()
        else:
            logger.warn("Either the config setting are incorrect ot the Tunnel to DB does not exist ... check")

    
    
    def set_use_env(self): # set the use environment from the config object
        file_handler = open(os.path.join(os.getcwd(), conn_config_file), 'rb')
        config_obj = pickle.load(file_handler)
        file_handler.close()
        self.default_use_env = config_obj.use_env
        self.use_location = self.default_use_env
        logger.info("Use location set to: " + self.use_location)

    
    
    def set_config_window(self):
        self.layout.itemAtPosition(1,1).widget().deleteLater()
        self.working_widget = configuration_window(self)
        self.layout.addWidget(self.working_widget,1,1)

        #self.working_widget.resize(self.working_widget.minimumSizeHint())
        self.working_widget.setMaximumHeight(500)
        self.resize(self.minimumSizeHint())
        self.layout.update()
        self.working_widget.closed.connect(self.show_project_info)

    
    
    def setup_DB_service(self):
        self.db_connection_obj = db_connection_obj()
        self.show_project_info()

    
    
    def setup_DUG_clients(self):
        self.DUG_connection_obj = DUG_connection_object(self.default_use_env)

    
    
    def setup_Tape_operation_manager(self):
        self.tape_operation_manager = Tape_operation_manager(self)

    
    
    def run_startup_sync_service(self):
        self.sync_service.sync_all()

    
    
    def setup_sync_service(self):
        self.sync_service = Synchronization_service(self)

    
    
    def sftp_transfer_necessary_files(self):
        transfer_base_64_encoder(self.DUG_connection_obj)
        transfer_SEGD_QC_parser_script(self.DUG_connection_obj)
        transfer_SEGY_check_script(self.DUG_connection_obj)
        transfer_run_daemons(self.DUG_connection_obj)
        transfer_run_log_fetcher(self.DUG_connection_obj)
        transfer_sgyt_encoder(self.DUG_connection_obj)

    
    
    def create_large_files_project_dir(self):
        logger.info("Now checking if the SEGY file dir for project exists in ../large_files")
        large_files_root_path = large_file_root_dict[self.use_location]
        project_name = self.db_connection_obj.db_name.split("_")[1]
        self.large_file_dir_proj_path = posixpath.join(large_files_root_path,project_name)
        status = check_generic_path(self.DUG_connection_obj,self.large_file_dir_proj_path)
        if status == 'True':
            logger.info(self.large_file_dir_proj_path + " :The directory already exists..")
        else:
            logger.info("Now creating ::" + self.large_file_dir_proj_path)
            create_generic_directory(self.DUG_connection_obj, self.large_file_dir_proj_path)
        self.DUG_connection_obj.large_files_dir = self.large_file_dir_proj_path

    
    
    def run_job_sync_service(self):
        run_sync_thread_name = self.thread_dict['dug'][0]
        self.run_sync_thread_to_use = self.thread_dict['dug'][1]
        dug_proj_path = str(self.DUG_connection_obj.DUG_proj_path)
        self.run_sync_service = run_information_sync(dug_proj_path=dug_proj_path, thread_name=run_sync_thread_name)
        self.run_sync_service.moveToThread(self.run_sync_thread_to_use)
        self.run_sync_thread_to_use.started.connect(self.run_sync_service.run_and_flush)
        logger.info(str("Starting Task execution sync service: " + run_sync_thread_name))
        self.run_sync_service.doingWork.connect(self.thread_dock.thread_control)
        self.run_sync_service.cmdcontrol.connect(self.run_sync_command)
        self.run_sync_service.update_tape_dashboard.connect(self.update_command_on_tape_dashboard)
        self.run_sync_thread_to_use.start_now()

    
    
    def run_sync_command(self, cmd):
        logger.info("Now executing : " + cmd)
        self.DUG_connection_obj.ts_client.exec_command(str(cmd))

    
    
    def application_refresh(self):
        """
        This is different from verified statrtup protocol as it only syncs application with database and does not create services again

        :return: None
        """
        if self.config_check is True:
            self.run_startup_sync_service()
            self.run_job_sync_service()
        else:
            logger.info("No valid configuration in use")

    
    
    def verified_start_up_protocol(self):

        self.set_use_env()
        self.config_status_signal.emit(True)

        self.setup_DB_service()

        self.setup_DUG_clients()
        self.sftp_transfer_necessary_files()

        self.create_large_files_project_dir()

        self.setup_Tape_operation_manager()

        self.setup_sync_service()

        self.run_startup_sync_service()

        self.run_job_sync_service()





#---------------------------------------------------------------------------------+
#home screen widget
#----------------------------------------------------------------------------------+
    
    
    def show_project_info(self): # show project information from orca
        if self.config_check ==True:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = project_info(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            #self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.setMaximumHeight(500)
            self.working_widget.closed.connect(self.show_project_info)
            self.layout.update()
        else:
            logger.info("No valid configuration in use ...")

# ----------------------------------------------------------------------------------+
#Functions related to setting up Deliverables
# ----------------------------------------------------------------------------------+

    
    
    def show_tape_dashboard(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.tape_dashboard_visible = True
            self.tape_dashboard = Tape_drive_dashboard(self)
            self.layout.addWidget(self.tape_dashboard, 3, 0, 1,4)
            self.update_command_on_tape_dashboard()

    
    
    def update_command_on_tape_dashboard(self):
        if self.tape_dashboard_visible == False:
            pass
        else:
            if os.path.exists(os.path.join(os.getcwd(),'temp','active_tasks')):
                file_handler = open(os.path.join(os.getcwd(),'temp','active_tasks'),'rb')
                task_dict = pickle.load(file_handler)
                file_handler.close()
                for a_dev in task_dict.keys():
                    if a_dev in self.tape_dashboard.tape_operation_manager.tape_service.available_dst:
                        self.tape_dashboard.dst_widget_dict[a_dev].clear()
                        self.tape_dashboard.dst_widget_dict[a_dev].append(task_dict[a_dev][0])
            else:
                pass

    
    
    def set_deliverables_window(self):
        if self.config_check ==False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = Deliverables_summary_window(self)
            self.layout.addWidget(self.working_widget, 1, 1)

            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.working_widget.setMinimumHeight(600)
            self.working_widget.setMinimumWidth(600)
            self.layout.update()
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_new_deliverable(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = add_new_deliverable(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_view_single_deliverable_detail(self,id):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = view_single_deliverable_detail(self,id)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_edit_single_deliverable_detail(self, id):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = edit_single_deliverable(self, id)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_usb_functions(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = usb_tools_window(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_add_usb_label(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = add_usb_label(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_edit_usb(self,id):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = edit_usb_window(self,id)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

    
    
    def set_usb_summary(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = usb_summary_window(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)

# --------------------------------------------------------------------------------+
#  Functions related to Shipments
# --------------------------------------------------------------------------------+

    
    
    def set_shipment_tools(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = shipment_tools(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())

    
    
    def set_shipments_summary(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = shipment_summary(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())

    
    
    def set_add_shipment(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = add_new_shipment(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())

    
    
    def set_edit_shipment(self,id):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = edit_shipment(self, id)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())
            self.working_widget.closed.connect(self.show_project_info)


#----------------------------------------------------------------------------------+

#--------------------------------------------------------------------------------+
# Functions related to SEGD
#---------------------------------------------------------------------------------

    
    
    def set_segd_tools_window(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = SEGD_tool_window(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())

    
    
    def set_survey_wide_SEGD_QC_summary(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.sync_service.SEGD_QC_sync()
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = refresh_enabled_SEGD_QC_summary(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())

    
    
    def run_SEGD_QC_summary_sync(self):
        logger.info("Now executing SEGD QC sync ..")
        self.sync_service.SEGD_QC_sync()
        logger.info("Done ..")
        self.set_survey_wide_SEGD_QC_summary()

    
    
    def set_segy_tools_window(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = SEGY_Tool_Window(self)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.layout.update()
            self.working_widget.resize(self.working_widget.minimumSizeHint())
            self.resize(self.minimumSizeHint())

    
    
    def set_segy_qc_status(self,deliverable):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            self.layout.itemAtPosition(1, 1).widget().deleteLater()
            self.working_widget = SEGY_qc_status(self,deliverable)
            self.layout.addWidget(self.working_widget, 1, 1)
            self.resize(self.minimumSizeHint())
            self.working_widget.setMinimumWidth(850)
            self.layout.update()
    
    
    def print_to_run_log(self, str_to_print):
        print self.thread1.isRunning()
        logger.info(str_to_print)

    
    
    def print_change_log_report(self):
        if self.config_check == False:
            logger.info("No valid configuration in use ...")
        else:
            if self.thread_dict['excel'][1].isRunning():
                self.print_to_run_log("The excel thread is busy.., please wait for T1 to finish working")
            else:
                file_name = str(str(datetime.datetime.now().strftime("%Y%m%d")) + "_change_log_report.xlsx")
                path = os.path.join(os.getcwd(),Report_dir,file_name)
                if os.path.exists(path):
                    os.remove(path)
                obj_list = self.db_connection_obj.sess.query(self.db_connection_obj.change_log).order_by(self.db_connection_obj.change_log.id_cl).all()
                self.thread_name = self.thread_dict['excel'][0]
                self.thread_to_use = self.thread_dict['excel'][1]
                # create the SEGD tape log report class object
                self.change_log_report = change_log_report(data= obj_list,file_name=file_name,thread_name=self.thread_name)
                # move the class on the thread that will perform the work
                self.change_log_report.moveToThread(self.thread_to_use)
                # click the start of the thread to the run funtion in the report class
                self.thread_to_use.started.connect(self.change_log_report.run)
                # connect the doing work signal in the report to the thread control in thread_dock for top window for status update and run time messaging
                self.change_log_report.doingWork.connect(self.thread_dock.thread_control)
                # connect the finished thread to the that will disconenct signals and disconenct the signal for the thread and keep it waiting
                self.change_log_report.finished.connect(self.finished_change_log_report)
                # send the meesage to the run time log
                self.print_to_run_log(
                    str("Creating change and delete log report fot the Survey on : " + self.thread_name))
                # start the run function on the thread muah ha ha ha ha ah !!!!!
                self.thread_to_use.start_work(self)

    
    
    def killThread(self,thread_type):
        thread = self.thread_dict[thread_type][1]
        thread.started.disconnect()
        thread.quit()
        thread.wait()

    
    
    def finished_change_log_report(self):
        self.change_log_report.finished.disconnect()
        self.change_log_report.doingWork.disconnect()
        self.killThread('excel')

    
    
    def closeEvent(self,event):
        self.closed.emit()
        #self.db_engine.dispose()
        try:
            self.db_connection_obj.db_engine.dispose()
            self.DUG_connection_obj.ws_client.close()
            self.DUG_connection_obj.ts_client.close()
            self.DUG_connection_obj.sftp_client.close()
            sys.exit()
        except:
            sys.exit()

