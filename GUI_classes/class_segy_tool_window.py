from general_functions.general_functions import create_center_data,create_central_labels, get_item_through_dialogue
from PyQt4 import QtGui, QtCore
from Tape_services.class_SEGY_service import SEGY_service
from database_engine.DB_ops import  get_list_of_SEGY_deliverables
from class_pop_up_combo_box import pop_up_combo_box
from database_engine.DB_ops import fetch_project_info
from class_reporter.class_SEGY_tape_log_report import SEGY_tape_log_header,SEGY_tape_log_report
from configuration import SEGY_tape_log_template_dict,Report_dir
import datetime, os
from configuration.Tool_tips import tool_tips_mapper_dict

class SEGY_Tool_Window(QtGui.QScrollArea):

    closed = QtCore.pyqtSignal()

    def __init__(self,parent):
        # define the top window

        super(SEGY_Tool_Window, self).__init__()
        self.parent = parent
        self.tool_tip_dict = tool_tips_mapper_dict['segy_tools']
        self.setToolTip(self.tool_tip_dict['general'])
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj
        self.SEGY_service = SEGY_service(self)

        grid = QtGui.QGridLayout()

        labels_widget = QtGui.QLabel('SEGY Tools') #position  = 0
        labels_widget.setAlignment(QtCore.Qt.AlignCenter)
        labels_widget.setStyleSheet('background-color: black; color: white')
        grid.addWidget(labels_widget, 0, 0)

        btn0 = QtGui.QPushButton("SEGY QC and production Status") #position = 1
        btn0.setToolTip(self.tool_tip_dict['status'])
        btn0.clicked.connect(self.segy_production_qc_status)
        btn0.resize(btn0.minimumSizeHint())
        grid.addWidget(btn0,1,0)

        lbl1 = create_central_labels('Report functions') #position = 2
        lbl1.resize(lbl1.minimumSizeHint())
        grid.addWidget(lbl1,2,0)

        btn1 = QtGui.QPushButton("Survey wide SEGY QC report")  # position = 3
        btn1.setToolTip(self.tool_tip_dict['survey_wide_qc'])
        btn1.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        btn1.resize(btn1.minimumSizeHint())
        grid.addWidget(btn1,3,0)


        btn2 = QtGui.QPushButton("Shipment wise SEGY QC report") #position = 4
        btn2.setToolTip(self.tool_tip_dict['shipment_wise_qc'])
        btn2.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        btn2.resize(btn2.minimumSizeHint())
        grid.addWidget(btn2,4,0)

        lbl2 = create_central_labels('DUG SEGY Templates') #position = 5
        lbl2.resize(lbl2.minimumSizeHint())
        grid.addWidget(lbl2,5,0)

        btn3 = QtGui.QPushButton("Create sequencewise DUGSGYT") #position = 6
        btn3.setToolTip(self.tool_tip_dict['2d_sgyt'])
        btn3.clicked.connect(self.DUG_SGYT)
        btn3.resize(btn3.minimumSizeHint())
        grid.addWidget(btn3,6,0)

        btn31 = QtGui.QPushButton("Create 3D DUGSGYT")  # position = 7
        btn31.setToolTip(self.tool_tip_dict['3d_sgyt'])
        btn31.clicked.connect(self.DUG_SGYT)
        btn31.resize(btn31.minimumSizeHint())
        grid.addWidget(btn31,7,0)


        lbl3 = create_central_labels('SEGY on disk QC') #postion = 8
        lbl3.resize(lbl3.minimumSizeHint())
        grid.addWidget(lbl3,8,0)

        btn4 = QtGui.QPushButton("Perform SEGY QC") #position = 9
        btn4.setToolTip(self.tool_tip_dict['segy_qc'])
        btn4.clicked.connect(self.single_SEGY_QC_perform)  ################## need to define proper funciton for this
        btn4.resize(btn4.minimumSizeHint())
        grid.addWidget(btn4,9,0)


        lbl4 = create_central_labels('Tape logs') #position = 10
        lbl4.resize(lbl4.minimumSizeHint())
        grid.addWidget(lbl4,10,0)

        btn6 = QtGui.QPushButton("Survey wide SEGY Tape Logs") #postion = 11
        btn6.setToolTip(self.tool_tip_dict['survey_wide_tape'])
        btn6.clicked.connect(self.survey_wide_tape_log)  ################## need to define proper funciton for this
        btn6.resize(btn6.minimumSizeHint())
        grid.addWidget(btn6,11,0)

        btn99 = QtGui.QPushButton("Shipment wise SEGY Tape Logs")  # postion = 11
        btn99.setToolTip(self.tool_tip_dict['shipment_tape'])
        btn99.clicked.connect(self.tool_welcome)  ################## need to define proper funciton for this
        btn99.resize(btn99.minimumSizeHint())
        grid.addWidget(btn99, 12, 0)

        for i in range(13,16):
            grid.addWidget(QtGui.QLabel(""),i,0)

        grid.setSpacing(10)
        self.setLayout(grid)
        self.resize(self.sizeHint())


    def tool_welcome(self):
        print "This function is not defined yet and will be available in the future "


    def DUG_SGYT(self):
        self.SEGY_service.create_sgyt()


    def single_SEGY_QC_perform(self):
        self.SEGY_service.perform_single_SEGY_QC()


    def segy_production_qc_status(self):
        self.choose_deliverable('SEGY_QC')


    def choose_deliverable(self, option):
        SEGY_deliverables_list = get_list_of_SEGY_deliverables(self.db_connection_obj)
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
        if ops == 'SEGY_QC':
            if caller == 'Deliverable':
                self.Deliverable = self.disp_name_dict[attribute]
                self.parent.set_segy_qc_status(self.Deliverable)
        if ops == 'Tape_log_survey_wide':
            if caller == 'Deliverable':
                self.Deliverable = self.disp_name_dict[attribute]
                self.no_of_sets = self.Deliverable.copies
                self.file_name = str(self.Deliverable.id) + "_" + str(
                    datetime.datetime.now().strftime("%Y%m%d")) + "_SEGY_Tape_log.xlsx"
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


    def survey_wide_tape_log(self):
        self.choose_deliverable('Tape_log_survey_wide')

    def print_tape_log_to_file(self,shipment_no):
        self.thread_type = 'excel'
        # get the list of all objects for the deliverable id
        obj_list = self.create_tape_log_entry_obj_list()
        # get the project information
        project_info = fetch_project_info(self.db_connection_obj)
        # create the header object
        header_obj = SEGY_tape_log_header(proj_info_obj=project_info[0], set_no=self.no_of_sets, shipment_no=shipment_no)
        # choose the worker thread
        if self.parent.thread_dict[self.thread_type][1].isRunning():
            self.parent.print_to_run_log("The excel thread is busy.., please wait for T1 to finish working")
        else:
            self.thread_name = self.parent.thread_dict['excel'][0]
            self.thread_to_use = self.parent.thread_dict['excel'][1]
            # create the SEGD tape log report class object
            template_name = SEGY_tape_log_template_dict[self.Deliverable.type]
            self.SEGY_tape_log_report = SEGY_tape_log_report(header=header_obj, data=obj_list, file_name=self.file_name,
                                                 thread_name=self.thread_name,template_name =template_name)
            # move the class on the thread that will perform the work
            self.SEGY_tape_log_report.moveToThread(self.thread_to_use)
            # click the start of the thread to the run funtion in the report class
            self.thread_to_use.started.connect(self.SEGY_tape_log_report.run)
            # connect the doing work signal in the report to the thread control in thread_dock for top window for status update and run time messaging
            self.SEGY_tape_log_report.doingWork.connect(self.parent.thread_dock.thread_control)
            # connect the finished thread to the that will disconenct signals and disconenct the signal for the thread and keep it waiting
            self.SEGY_tape_log_report.finished.connect(self.finished_SEGY_tape_log_report)
            # send the meesage to the run time log
            self.parent.print_to_run_log(str("Creating SEGD Tape log report fot the Survey on : " + self.thread_name))
            # start the run function on the thread muah ha ha ha ha ah !!!!!
            self.thread_to_use.start_work(self)



    def finished_SEGY_tape_log_report(self):
        self.SEGY_tape_log_report.finished.disconnect()
        self.SEGY_tape_log_report.doingWork.disconnect()
        self.parent.killThread(self.thread_type)


    def create_tape_log_entry_obj_list(self):
        # The root needs to come from media list and only there we have a list of SEGY write approved item list
        SEGY_media_list = self.db_connection_obj.sess.query(
            self.db_connection_obj.Media_list).filter(self.db_connection_obj.Media_list.deliverable_id == self.Deliverable.id).order_by(self.db_connection_obj.Media_list.reel_no).all()
        if self.Deliverable.media in ['3592 JA','3592 JC']: # This is the simplest of the cases and should deal with Navmerge SEGY our top priority
            # Now simply use the reel number which should be 1:1 as media with only one SEGY per tape

            SEGY_on_disk_qc_obj_list = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
                self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.Deliverable.id
            ).all()
            # Now create the dict object for this
            SEGY_on_disk_qc_dict = {} # Reel_no, object
            for obj in SEGY_on_disk_qc_obj_list:
                SEGY_on_disk_qc_dict.update({obj.sgyt_reel_no : obj})
            obj_list_for_report = []
            for i in range(0,len(SEGY_media_list)): # To keep it in order of tape number
                obj_list_for_report.append(Tape_log_entry_tape_1_1(SEGY_media_list[i],SEGY_on_disk_qc_dict[SEGY_media_list[i].reel_no]))

        return obj_list_for_report


class Tape_log_entry_tape_1_1(object):
    def __init__(self, media_list_obj, segy_qc_obj):
        self.reel_no = media_list_obj.reel_no
        self.media_label = media_list_obj.media_label
        self.line_name = segy_qc_obj.line_name
        self.sgyt_min_ffid = segy_qc_obj.sgyt_min_ffid
        self.set_no = media_list_obj.set_no
        self.sgyt_max_ffid = segy_qc_obj.sgyt_max_ffid
        self.sgyt_fgsp = segy_qc_obj.sgyt_fgsp
        self.sgyt_lgsp = segy_qc_obj.sgyt_lgsp
        self.sgyt_min_il = segy_qc_obj.sgyt_min_il
        self.sgyt_max_il = segy_qc_obj.sgyt_max_il
        self.sgyt_min_xl = segy_qc_obj.sgyt_min_xl
        self.sgyt_max_xl = segy_qc_obj.sgyt_max_xl
        self.shipment_no = media_list_obj.shipment_no
        self.box_no = media_list_obj.box_no
        self.use_tag = media_list_obj.use_tag

