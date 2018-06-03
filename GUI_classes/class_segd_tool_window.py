
#----------class_imports -----
from PyQt4 import QtGui, QtCore
from general_functions.general_functions import get_item_through_dialogue
from database_engine.DB_ops import get_list_of_segd_deliverables, get_SEGD_QC_object_list_for_deliverable_set,fetch_project_info,fetch_seq_name_from_id, get_all_SEGD_QC_for_deliverable
from GUI_classes.class_pop_up_combo_box import pop_up_combo_box
import datetime
import os
from class_reporter.class_SEGD_QC_report import SEGD_QC_header, SEGD_QC_report
from class_reporter.class_SEGD_tape_log_report import SEGD_tape_log_header,SEGD_tape_log_report
from configuration import Report_dir
from configuration.Tool_tips import tool_tips_mapper_dict

#-----------------------------
class SEGD_tool_window(QtGui.QScrollArea):

    closed = QtCore.pyqtSignal()

    def __init__(self,parent):
        # define the top window

        super(SEGD_tool_window, self).__init__(parent=parent)
        self.tool_tip_dict = tool_tips_mapper_dict['segd_tools']
        self.setToolTip(self.tool_tip_dict['general'])
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid = QtGui.QGridLayout()

        btn2 = QtGui.QPushButton("Show Status Report", self)
        btn2.setToolTip(self.tool_tip_dict['show_status'])
        btn2.clicked.connect(self.parent.set_survey_wide_SEGD_QC_summary)  ################## need to define proper funciton for this
        btn2.resize(btn2.minimumSizeHint())


        # btn3 = QtGui.QPushButton("QC SEGD Tape", self)
        # btn3.setStatusTip('QC a single SEGD Tape ')
        # btn3.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        # btn3.resize(btn3.minimumSizeHint())
        #
        #
        # btn4 = QtGui.QPushButton("Verify QC report", self)
        # btn4.setStatusTip('Verify QC report for a single sequence')
        # btn4.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        # btn4.resize(btn4.minimumSizeHint())

        btn5 = QtGui.QPushButton("Survey wide QC report", self)
        btn5.setToolTip(self.tool_tip_dict['survey_wide_qc'])
        btn5.clicked.connect(self.survey_wide_qc_report)  ################## need to define proper funciton for this
        btn5.resize(btn5.minimumSizeHint())

        btn6 = QtGui.QPushButton("Survey wide Tape log", self)
        btn6.setToolTip(self.tool_tip_dict['survey_wide_tape'])
        btn6.clicked.connect(self.survey_wide_tape_log)  ################## need to define proper funciton for this
        btn6.resize(btn6.minimumSizeHint())

        btn7 = QtGui.QPushButton("Shipment QC report ", self)
        btn7.setToolTip(self.tool_tip_dict['shipment_qc'])
        btn7.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        btn7.resize(btn7.minimumSizeHint())

        btn8 = QtGui.QPushButton("Shipment Tape Logs", self)
        btn8.setToolTip(self.tool_tip_dict['shipment_tape'])
        btn8.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        btn8.resize(btn8.minimumSizeHint())

        labels_widget = QtGui.QLabel('SEGD Tools')
        labels_widget.setAlignment(QtCore.Qt.AlignCenter)
        labels_widget.setStyleSheet('background-color: black; color: white')
        grid.addWidget(labels_widget,0,0)
        grid.addWidget(btn2,1,0)
        # grid.addWidget(btn3, 2, 0)
        # grid.addWidget(btn4, 3,0)

        grid.addWidget(btn5, 2, 0)
        grid.addWidget(btn6, 3, 0)
        grid.addWidget(btn7, 4, 0)
        grid.addWidget(btn8, 5, 0)

        self.thread_type = 'excel'

        for i in range (6,16):
            grid.addWidget(QtGui.QLabel(""),i,0)

        grid.setSpacing(10)
        self.setLayout(grid)
        self.resize(self.sizeHint())


    def tool_welcome(self):
        print "This function is not defined yet and will be available in the future "


    def survey_wide_qc_report(self):
        self.choose_deliverable('SEGD_QC_report')


    def survey_wide_tape_log(self):
        self.choose_deliverable('SEGD_tape_log')


    def choose_deliverable(self, option):
        SEGY_deliverables_list = get_list_of_segd_deliverables(self.db_connection_obj)
        disp_name_dict = {}
        combo_item_list = []
        for deliverable in SEGY_deliverables_list:
            key = str(deliverable.id) + "_" + deliverable.name
            data = deliverable
            disp_name_dict.update({key: data})
            combo_item_list.append(key)

        self.disp_name_dict = disp_name_dict
        self.pop_up_combo_box = pop_up_combo_box(self, "Select deliverable", combo_item_list, 'Deliverable', option)
        self.pop_up_combo_box.show()


    def set_attribute(self, attribute, caller, ops):
        if ops == 'SEGD_QC_report':
            if caller == 'Deliverable':
                self.deliverable = self.disp_name_dict[attribute]
                self.no_of_sets = self.deliverable.copies
                self.file_name = str(self.deliverable.id) + "_" + str(datetime.datetime.now().strftime ("%Y%m%d")) + "_SEGD_QC_report.xlsx"
                self.file_path = os.path.join(os.getcwd(),Report_dir,self.file_name)
                if os.path.exists(self.file_path):
                    print "A file with the same name exists, do you want to overwrite it ? type y to continue .."
                    message = "Type y to continue "
                    choice = get_item_through_dialogue(self, message)
                    if choice == 'y':
                        os.remove(self.file_path)
                        self.print_report_to_file('survey-wide')
                else:
                    self.print_report_to_file('survey-wide')
        elif ops == 'SEGD_tape_log':
            if caller == 'Deliverable':
                self.deliverable = self.disp_name_dict[attribute]
                self.no_of_sets = self.deliverable.copies
                self.file_name = str(self.deliverable.id) + "_" + str(
                    datetime.datetime.now().strftime("%Y%m%d")) + "_SEGD_Tape_log.xlsx"
                self.file_path = os.path.join(os.getcwd(), Report_dir, self.file_name)
                if os.path.exists(self.file_path):
                    print "A file with the same name exists, do you want to overwrite it ? type y to continue .."
                    message = "Type y to continue "
                    choice = get_item_through_dialogue(self, message)
                    if choice == 'y':
                        os.remove(self.file_path)
                        self.print_tape_log_to_file('survey-wide')
                else:
                    self.print_tape_log_to_file('survey-wide')


    def print_report_to_file(self,shipment_no):
        # get the list of all QC objects for the deliverable id
        obj_list = get_all_SEGD_QC_for_deliverable(self.db_connection_obj, self.deliverable.id)
        # get the project information
        project_info = fetch_project_info(self.db_connection_obj)
        # create the header object
        header_obj = SEGD_QC_header(proj_info_obj=project_info[0], set_no= self.no_of_sets, shipment_no = shipment_no)
        #choose the worker thread
        if self.parent.thread_dict[self.thread_type][1].isRunning():
            self.parent.print_to_run_log("The excel thread is busy.., please wait for T1 to finish working")
        else:
            self.thread_name = self.parent.thread_dict['excel'][0]
            self.thread_to_use = self.parent.thread_dict['excel'][1]
            #create the SEGD QC class object
            self.SEGD_QC_report = SEGD_QC_report(header=header_obj, data=obj_list, file_name=self.file_name,thread_name = self.thread_name)
            #move the class on the thread that will perform the work
            self.SEGD_QC_report.moveToThread(self.thread_to_use)
            # click the start of the thread to the run funtion in the report class
            self.thread_to_use.started.connect(self.SEGD_QC_report.run)
            # connect the doing work signal in the report to the thread control in thread_dock for top window for status update and run time messaging
            self.SEGD_QC_report.doingWork.connect(self.parent.thread_dock.thread_control)
            # connect the finished thread to the that will disconenct signals and disconenct the signal for the thread and keep it waiting
            self.SEGD_QC_report.finished.connect(self.finished_SEGD_QC_report)
            # send the meesage to the run time log
            self.parent.print_to_run_log(str("Creating SEGD QC report fot the Survey on : " + self.thread_name))
            # start the run function on the thread muah ha ha ha ha ah !!!!!
            self.thread_to_use.start_work(self)


    def print_tape_log_to_file(self,shipment_no):
        # get the list of all objects for the deliverable id
        obj_list = self.create_tape_log_entry_obj_list()
        # get the project information
        project_info = fetch_project_info(self.db_connection_obj)
        # create the header object
        header_obj = SEGD_tape_log_header(proj_info_obj=project_info[0], set_no=self.no_of_sets, shipment_no=shipment_no)
        # choose the worker thread
        if self.parent.thread_dict[self.thread_type][1].isRunning():
            self.parent.print_to_run_log("The excel thread is busy.., please wait for T1 to finish working")
        else:
            self.thread_name = self.parent.thread_dict['excel'][0]
            self.thread_to_use = self.parent.thread_dict['excel'][1]
            # create the SEGD tape log report class object
            self.SEGD_tape_log_report = SEGD_tape_log_report(header=header_obj, data=obj_list, file_name=self.file_name,
                                                 thread_name=self.thread_name)
            # move the class on the thread that will perform the work
            self.SEGD_tape_log_report.moveToThread(self.thread_to_use)
            # click the start of the thread to the run funtion in the report class
            self.thread_to_use.started.connect(self.SEGD_tape_log_report.run)
            # connect the doing work signal in the report to the thread control in thread_dock for top window for status update and run time messaging
            self.SEGD_tape_log_report.doingWork.connect(self.parent.thread_dock.thread_control)
            # connect the finished thread to the that will disconenct signals and disconenct the signal for the thread and keep it waiting
            self.SEGD_tape_log_report.finished.connect(self.finished_SEGD_tape_log_report)
            # send the meesage to the run time log
            self.parent.print_to_run_log(str("Creating SEGD Tape log report fot the Survey on : " + self.thread_name))
            # start the run function on the thread muah ha ha ha ha ah !!!!!
            self.thread_to_use.start_work(self)



    def finished_SEGD_QC_report(self):
        self.SEGD_QC_report.finished.disconnect()
        self.SEGD_QC_report.doingWork.disconnect()
        self.parent.killThread(self.thread_type)

    def finished_SEGD_tape_log_report(self):
        self.SEGD_tape_log_report.finished.disconnect()
        self.SEGD_tape_log_report.doingWork.disconnect()
        self.parent.killThread(self.thread_type)



    def create_tape_log_entry_obj_list(self):
        obj = self.db_connection_obj # simply to make the code shorter
        tape_log_entry_list = []
        tape_list = obj.sess.query(obj.SEGD_tapes).all()
        seq_info_list = obj.sess.query(obj.Line).all()
        seq_dict = {}
        for seq_entry in seq_info_list:
            key = str(seq_entry.sequence_number)
            data = seq_entry
            seq_dict.update({key:data})
        tape_dict = {}
        for tape in tape_list:
            key = tape.name
            data = tape
            tape_dict.update({key:data})
        media_list = obj.sess.query(obj.Media_list).filter(obj.Media_list.deliverable_id == self.deliverable.id).all()
        for media in media_list:
            tape_log_entry_list.append(Tape_log_entry(media,tape_dict[media.reel_no],seq_dict[str(tape_dict[media.reel_no].sequence_number)]))

        return tape_log_entry_list


class Tape_log_entry(object):
    def __init__(self,media_list_obj,tape_obj,seq_obj):
        self.tape_no = media_list_obj.reel_no
        self.line_name = seq_obj.real_line_name
        self.f_ffid = tape_obj.first_ffid
        self.l_ffid = tape_obj.last_ffid
        self.fsp = tape_obj.first_shot_number
        self.lsp = tape_obj.last_shot_number
        self.shipment_no = media_list_obj.shipment_no
        self.box_no = media_list_obj.box_no
        self.set_no = media_list_obj.set_no












