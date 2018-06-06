from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels
from class_pop_up_message_box import pop_up_message_box
from database_engine.DB_ops import get_seq_list_from_line_name_list
from configuration import multiple_per_tape_list

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class SEGD_QC_Form(QtGui.QWidget):

    def __init__(self,parent):
        super(SEGD_QC_Form, self).__init__()
        #parent
        self.parent = parent


        #grid
        self.grid = QtGui.QGridLayout()
        self.setWindowTitle("SEGD QC Input form")

        self.db_connection_obj = self.parent.tape_operation_manager.db_connection_obj
        # labels

        self.grid.addWidget(create_central_labels('SEGD QC Input'),0,0,1,3)
        self.grid.addWidget(create_central_labels('Select Drive'),1,0)
        self.grid.addWidget(create_central_labels('Select Deliverable'),2,0)
        self.grid.addWidget(create_central_labels('Select line'),4,0)
        self.grid.addWidget(create_central_labels('Select set'),3,0)
        self.grid.addWidget(create_central_labels('Select Tape'),5,0)
        self.grid.addWidget(create_central_labels('Confirm Tape'),6,0)


        # pushbuttons


        self.pb_execute = QtGui.QPushButton('Run')
        self.grid.addWidget(self.pb_execute,9,0)
        self.pb_execute.clicked.connect(self.execute)


        # combo boxes

        self.combo_tape_drive = QtGui.QComboBox()
        self.combo_tape_drive.setObjectName("Tape Drive")
        self.grid.addWidget(self.combo_tape_drive,1,1)
        self.combo_tape_drive.addItems(self.parent.tape_operation_manager.tape_service.available_dst)
        self.combo_tape_drive.setCurrentIndex(-1)
        self.combo_tape_drive.blockSignals(False)
        self.combo_tape_drive.currentIndexChanged.connect(self.tape_drive_selected)



        self.combo_deliverable = QtGui.QComboBox()
        self.combo_deliverable.setObjectName("Deliverable")
        self.grid.addWidget(self.combo_deliverable,2,1)
        self.combo_deliverable.addItems(self.parent.tape_operation_manager.get_available_segd_deliverable_list())
        self.combo_deliverable.setCurrentIndex(-1)
        self.combo_deliverable.blockSignals(False)
        self.combo_deliverable.currentIndexChanged.connect(self.deliverable_selected)

        self.combo_line = file_selection(self)
        self.combo_line.setObjectName("File name")
        self.combo_line.setFixedHeight(400)
        self.grid.addWidget(self.combo_line, 4, 1, 1, 2)


        self.combo_set = QtGui.QComboBox()
        self.combo_set.setObjectName("Set no")
        self.grid.addWidget(self.combo_set,3,1)
        self.combo_set.blockSignals(True)
        self.combo_set.currentIndexChanged.connect(self.set_selected)


        self.combo_tape = QtGui.QComboBox()
        self.combo_tape.setObjectName("Tape no")
        self.grid.addWidget(self.combo_tape,5,1)
        self.combo_tape.blockSignals(True)
        self.combo_tape.currentIndexChanged.connect(self.tape_selected)


        self.line_tape = QtGui.QLineEdit()
        self.grid.addWidget(self.line_tape,6,1)

        self.chk_locked = QtGui.QCheckBox("Tape locked")
        self.grid.addWidget(self.chk_locked,7,1)


        self.chk_label = QtGui.QCheckBox("Label checked")
        self.grid.addWidget(self.chk_label,8,1)

        self.setLayout(self.grid)


    def tape_drive_selected(self):
        dst = str(self.combo_tape_drive.currentText())
        logger.info("Setting tape drive to: " + dst)


    def deliverable_selected(self):
        if self.combo_deliverable.currentIndex() == -1:
            self.set_no = None
            self.combo_set.clear()
            self.combo_set.setCurrentIndex(-1)
        else:
            deliverable = str(self.combo_deliverable.currentText())
            self.parent.tape_operation_manager.set_deliverable(deliverable)
            self.deliverable = deliverable
            print "Deliverable is set to: " + deliverable
            self.combo_set.clear()
            self.combo_set.setCurrentIndex(-1)
            self.combo_set.blockSignals(True)
            self.combo_set.addItems(self.parent.tape_operation_manager.get_deliverable_set_list())
            self.combo_set.setCurrentIndex(-1)
            self.combo_set.blockSignals(False)
            self.combo_line.add_dummy_widget()
            self.combo_line.setStyleSheet('background-color: None')
            self.update()



    def set_selected(self):
        if int(self.combo_set.currentIndex()) == -1:
            pass
        else:
            set_no = str(self.combo_set.currentText())
            self.parent.tape_operation_manager.set_working_set(set_no)
            logger.info("Set no is set to: " + str(set_no))
            file_list  = self.parent.tape_operation_manager.service_class.get_list_of_available_segd_seq()
            file_list_removed = self.parent.tape_operation_manager.service_class.get_list_of_unchecked_SEGD_seq_for_set(file_list)
            self.sort_file_list(file_list, 'all')
            self.sort_file_list(file_list_removed, 'removed')
            self.combo_line.toggle_file_selection()
            self.update()


    def sort_file_list(self,file_list,list_items):
        seq_dict = get_seq_list_from_line_name_list(self.db_connection_obj, file_list)
        seq_sorted = sorted(seq_dict.keys())
        if list_items == 'all':
            self.line_list = []
            for index in range(0, len(seq_sorted)):
                self.line_list.append(seq_dict[seq_sorted[index]])
        elif list_items == 'removed':
            self.unchecked_line_list = []
            for index in range(0, len(seq_sorted)):
                self.unchecked_line_list.append(seq_dict[seq_sorted[index]])

    def line_selected(self):
            self.combo_tape.clear()
            self.combo_tape.addItems(self.parent.tape_operation_manager.service_class.get_list_of_applicable_segd_tapes(file_list=self.segd_qc_line_list))
            self.combo_tape.setCurrentIndex(-1)
            self.combo_tape.blockSignals(False)


    def tape_selected(self):
        if int(self.combo_tape.currentIndex()) == -1:
            pass
        else:
            tape = str(self.combo_tape.currentText())
            logger.info("Tape is set to: " + tape)


    def execute(self):
        self.combo_list = [
            self.combo_tape_drive,
            self.combo_deliverable,
            self.combo_set,
            self.combo_tape,
        ]
        combo_entry_check = True
        for a_combo in self.combo_list:
            if a_combo.currentIndex() == -1:
                combo_entry_check = False
                logger.warning(str(a_combo.objectName()) + " : Is blank aborting")

        if combo_entry_check == True:
            if self.file_selected == True:
                if self.chk_locked.isChecked() is True:
                    if self.chk_label.isChecked() is True:
                        dst = str(self.combo_tape_drive.currentText())
                        deliverable = str(self.combo_deliverable.currentText())
                        set_no = str(self.combo_set.currentText())
                        reel_no = str(self.combo_tape.currentText())
                        # Now perform tape manual vs auto check
                        if str(self.combo_tape.currentText()) == str(self.line_tape.text()):
                            logger.info("Ok to run")
                            self.parent.SEGD_QC_execute(reel_no=reel_no, file_list= self.segd_qc_line_list, deliverable= deliverable, drive=dst, set=set_no, split_line = self.split_line)
                            self.close()
                        else:
                            logger.warning("Manual and Db entries for tape do not match")
                    else:
                        logger.warning("Please make sure that you have checked the label")
                else:
                    logger.warning("Please make sure that the SEGD tape is locked !!")
            else:
                logger.warning("Please select file 1st")



class file_selection(QtGui.QWidget):

    def __init__(self,parent):
        super(file_selection,self).__init__()
        self.parent = parent

        self.grid = QtGui.QGridLayout()

        self.parent.file_selected = False

        self.pb_ok = QtGui.QPushButton('Confirm selection')
        self.pb_ok.clicked.connect(self.ok_exit)
        self.grid.addWidget(self.pb_ok, 0, 0)

        self.ck_box_remove = QtGui.QCheckBox('Remove files already checked')
        self.grid.addWidget(self.ck_box_remove, 1, 0)
        self.ck_box_remove.stateChanged.connect(self.toggle_file_selection)

        self.grid.addWidget(create_central_labels("Files"), 2, 0)

        self.setLayout(self.grid)
        self.show()


    def add_dummy_widget(self):
        self.working_widet = QtGui.QScrollArea()
        self.grid.addWidget(self.working_widet,3,0)
        self.update_routine()

    def add_all_files_widget(self):
        self.working_widget = all_files_widget(self.parent)
        self.grid.addWidget(self.working_widget, 3, 0)
        self.working_widget.closed.connect(self.add_unwritten_files_widget)
        self.update_routine()

    def add_unwritten_files_widget(self):
        self.working_widet = unwritten_files_widget(self.parent)
        self.grid.addWidget(self.working_widet, 3, 0)
        self.working_widget.closed.connect(self.add_all_files_widget)
        self.update_routine()

    def update_routine(self):
        self.setStyleSheet('background-color: None')
        self.grid.update()
        self.update()
        self.parent.update()


    def toggle_file_selection(self):
        if self.ck_box_remove.isChecked() == True:
            self.grid.itemAtPosition(3,0).widget().deleteLater()
            self.add_unwritten_files_widget()
        else:
            self.grid.itemAtPosition(3, 0).widget().deleteLater()
            self.add_all_files_widget()


    def calculate_combined_file_size(self,return_list):
        self.file_size = 0
        for a_file in return_list:
            self.file_size = self.file_size + self.parent.file_size_dict[a_file]

    def ok_exit(self):
        return_list = []
        for i in range(len(self.btn_list)):
            if self.btn_list[i].isChecked() is True:
                return_list.append(str(self.btn_list[i].objectName()))
        if len(return_list) == 0:
            warning_message = "No file selected !!"
            self.warning_pop_up = pop_up_message_box(warning_message, 'Warning')
            self.warning_pop_up.show()
        else:
            if self.parent.parent.tape_operation_manager.deliverable.media not in multiple_per_tape_list:
                if len(return_list) > 1:
                    warning_message = "This deliverable media file does not support multiple files per tape, if you indend to do so, please change deliverable media type first !!"
                    self.warning_pop_up = pop_up_message_box(warning_message, 'Warning')
                    self.warning_pop_up.show()
                else:
                    self.parent.split_line = True
                    self.parent.segd_qc_line_list = return_list
                    self.setStyleSheet('background-color: green')
                    self.parent.file_selected = True
                    self.parent.line_selected()
            else:
                self.parent.split_line = False
                self.parent.segd_qc_line_list = return_list
                self.setStyleSheet('background-color: green')
                self.parent.file_selected = True
                self.parent.line_selected()



class all_files_widget(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()
    def __init__(self,parent):
        super(all_files_widget, self).__init__()
        self.parent = parent
        self.grid = QtGui.QGridLayout()
        self.widget  = QtGui.QWidget()
        i = 0
        self.parent.combo_line.btn_list = []
        for a_file in self.parent.line_list:
            btn = QtGui.QCheckBox(a_file)
            btn.setObjectName(a_file)
            self.grid.addWidget(btn, i, 0)
            self.parent.combo_line.btn_list.append(btn)
            i = i + 1
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)



class unwritten_files_widget(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()
    def __init__(self,parent):
        super(unwritten_files_widget, self).__init__()
        self.parent = parent
        self.grid = QtGui.QGridLayout()
        i = 0
        self.parent.combo_line.btn_list = []
        self.widget = QtGui.QWidget()
        for a_file in self.parent.unchecked_line_list:
            btn = QtGui.QCheckBox(a_file)
            btn.setObjectName(a_file)
            self.grid.addWidget(btn, i, 0)
            self.parent.combo_line.btn_list.append(btn)
            i = i + 1
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)




