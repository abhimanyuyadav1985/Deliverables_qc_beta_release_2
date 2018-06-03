#----------class_imports -----
from general_functions.general_functions import *
from configuration.Tool_tips import tool_tips_mapper_dict
from class_bug_reporter import bug_reporter
from GUI_classes.class_task_information import running_task_log
import time
#-----------------------------
####################################################################################################################################
####Left Widget
####################################################################################################################################
class left_dock(QtGui.QWidget):
    def __init__(self,parent):
        # define the top window
        super(left_dock, self).__init__(parent=parent)
        self.db_status = []
        # create the status bar
        self.parent = parent
        self.tool_available = 0
        self.setWindowTitle("Options")
        self.tool_tip_dict = tool_tips_mapper_dict['main_menu']

        #Connection button
        self.pb_config = QtGui.QPushButton("Configuration", self)
        self.pb_config.resize(self.pb_config.minimumSizeHint())
        self.pb_config.setToolTip(self.tool_tip_dict['configuration'])

        # Deliverables button
        self.pb_deliverables = QtGui.QPushButton("Deliverables", self)
        self.pb_deliverables.resize(self.pb_deliverables.minimumSizeHint())
        self.pb_deliverables.setToolTip(self.tool_tip_dict['deliverables'])

        #Tape drive dashboard

        self.pb_tape_home = QtGui.QPushButton("Tape Dashboard",self)
        self.pb_tape_home.resize(self.pb_deliverables.minimumSizeHint())
        self.pb_tape_home.clicked.connect(self.parent.show_tape_dashboard)
        self.pb_tape_home.setToolTip(self.tool_tip_dict['tape_dashboard'])

        # SEGD button
        self.pb_segd = QtGui.QPushButton("SEGD Toolkit", self)
        self.pb_segd.resize(self.pb_segd.minimumSizeHint())
        self.pb_segd.setToolTip(self.tool_tip_dict['segd_tools'])

        # SEGD button
        self.pb_segy = QtGui.QPushButton("SEGY Toolkit", self)
        self.pb_segy.resize(self.pb_segy.minimumSizeHint())
        self.pb_segy.setToolTip(self.tool_tip_dict['segy_tools'])

        # refresh button
        self.pb_refresh = QtGui.QPushButton("Refresh", self)
        self.pb_refresh.resize(self.pb_refresh.minimumSizeHint())
        self.pb_refresh.setToolTip(self.tool_tip_dict['refresh'])

        self.pb_home = QtGui.QPushButton()
        self.pb_home.setText('Home')
        self.pb_home.clicked.connect(self.parent.show_project_info)
        self.pb_home.setToolTip(self.tool_tip_dict['home'])

        # create the button to quit
        self.pb_quit = QtGui.QPushButton("Quit", self)
        self.pb_quit.resize(self.pb_quit.minimumSizeHint())
        self.pb_quit.setToolTip(self.tool_tip_dict['quit'])


        self.pb_deliverables.clicked.connect(self.parent.set_deliverables_window)
        self.pb_segd.clicked.connect(self.parent.set_segd_tools_window)
        self.pb_segy.clicked.connect(self.parent.set_segy_tools_window)


        self.pb_config.clicked.connect(self.parent.set_config_window)
        self.pb_refresh.clicked.connect(self.parent.application_refresh)
        self.pb_quit.clicked.connect(self.parent.closeEvent)


        self.pb_shipments = QtGui.QPushButton("Shipments")
        self.pb_shipments.clicked.connect(self.parent.set_shipment_tools)
        self.pb_shipments.setToolTip(self.tool_tip_dict['shipments'])

        self.pb_usb = QtGui.QPushButton("USB functions")
        self.pb_usb.setToolTip(self.tool_tip_dict['usb_tools'])
        self.pb_usb.clicked.connect(self.parent.set_usb_functions)

        self.pb_change_log = QtGui.QPushButton("Change log Report")
        self.pb_change_log.clicked.connect(self.parent.print_change_log_report)
        self.pb_change_log.setToolTip(self.tool_tip_dict['change_log'])


        self.pb_bug_report = QtGui.QPushButton('Bug report')
        self.pb_bug_report.clicked.connect(self.support_request)
        self.pb_bug_report.setToolTip(self.tool_tip_dict['bug_report'])


        self.pb_run_info = QtGui.QPushButton('Active task logs')
        self.pb_run_info.clicked.connect(self.active_task_info)

        self.pb_connect = QtGui.QPushButton('Connect')
        self.pb_connect.clicked.connect(self.parent.check_existing_config)


        grid = QtGui.QGridLayout()
        dock_label = create_central_labels("Main Menu")
        grid.addWidget(dock_label,0,0)
        grid.addWidget(self.pb_config,1,0)
        grid.addWidget(self.pb_deliverables, 2, 0)
        grid.addWidget(self.pb_usb,6,0)
        grid.addWidget(self.pb_tape_home,3,0)
        grid.addWidget(self.pb_segd, 4, 0)
        grid.addWidget(self.pb_segy,5,0)
        grid.addWidget(self.pb_shipments,7,0)
        grid.addWidget(self.pb_run_info,8,0)
        grid.addWidget(self.pb_refresh, 9, 0)
        grid.addWidget(create_central_labels('Admin'),10,0)
        grid.addWidget(self.pb_connect,11,0)
        grid.addWidget(self.pb_home,12,0)
        grid.addWidget(self.pb_change_log,13,0)
        grid.addWidget(self.pb_bug_report,14,0)
        grid.addWidget(self.pb_quit, 15, 0)
        grid.setSpacing(10)
        self.setLayout(grid)
        self.resize(self.sizeHint())

    def nouse(self):
        print "Please use the refresh button to activate config file and initialize tools.."


    def active_task_info(self):
        if self.parent.config_check == True:
            self.active_run_logs = running_task_log(self.parent)
            self.active_run_logs.setMinimumWidth(200)
            self.active_run_logs.setMaximumHeight(800)
            self.active_run_logs.show()
        else:
            print "Please press the connect button to load an existng configuration first !!"

    def support_request(self):
        self.support_page = bug_reporter()
        self.support_page.show()
