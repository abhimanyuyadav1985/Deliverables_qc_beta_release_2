from PyQt4 import QtGui,QtCore
from class_pop_up_message_box import pop_up_message_box
from configuration import multiple_per_tape_list
from configuration import file_size_allowed_dict
from general_functions.general_functions import change_log_creation, create_central_labels

class segy_write_multiple(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(segy_write_multiple, self).__init__()
        self.parent = parent
        self.file_selected = False
        self.file_list = []
        self.segy_to_write_list = []

        self.grid = QtGui.QGridLayout()
        self.setWindowTitle("SEGY write Input form")

        # labels

        self.grid.addWidget(create_central_labels('SEGY write Input'), 0, 0, 1, 3)
        self.grid.addWidget(create_central_labels('Select Drive'), 1, 0)
        self.grid.addWidget(create_central_labels('Select Deliverable'), 2, 0)
        self.grid.addWidget(create_central_labels('Select File/s'), 4, 0)
        self.grid.addWidget(create_central_labels('Select set'), 3, 0)
        self.grid.addWidget(create_central_labels('Tape label'), 5, 0)
        self.grid.addWidget(create_central_labels("Media capacity (Mib)"),6,0)
        self.grid.addWidget(create_central_labels("Total size selected (Mib)"),7,0)

        # Labels
        self.label_media_capacity = QtGui.QLabel()
        self.grid.addWidget(self.label_media_capacity,6,1)

        self.selected_size = QtGui.QLabel()
        self.grid.addWidget(self.selected_size,7,1)

        # pushbuttons
        self.pb_execute = QtGui.QPushButton('Run')
        self.grid.addWidget(self.pb_execute, 8, 2)
        self.pb_execute.clicked.connect(self.execute)

        # combo boxes

        self.combo_tape_drive = QtGui.QComboBox()
        self.combo_tape_drive.setObjectName("Tape Drive")
        self.grid.addWidget(self.combo_tape_drive, 1, 1,1,2)
        self.combo_tape_drive.addItems(self.parent.tape_operation_manager.tape_service.available_dst)
        self.combo_tape_drive.setCurrentIndex(-1)
        self.combo_tape_drive.blockSignals(False)
        self.combo_tape_drive.currentIndexChanged.connect(self.tape_drive_selected)

        self.combo_deliverable = QtGui.QComboBox()
        self.combo_deliverable.setObjectName("Deliverable")
        self.grid.addWidget(self.combo_deliverable, 2, 1,1,2)
        self.combo_deliverable.addItems(self.parent.tape_operation_manager.get_all_SEGY_tape_write_deliverable_list())
        self.combo_deliverable.setCurrentIndex(-1)
        self.combo_deliverable.blockSignals(False)
        self.combo_deliverable.currentIndexChanged.connect(self.deliverable_selected)

        self.combo_line = file_selection(self)
        self.combo_line.setObjectName("File name")
        self.combo_line.setFixedHeight(400)
        self.grid.addWidget(self.combo_line, 4, 1, 1, 2)


        self.combo_set = QtGui.QComboBox()
        self.combo_set.setObjectName("Set no")
        self.grid.addWidget(self.combo_set, 3, 1,1,2)

        self.combo_set.blockSignals(True)
        self.combo_set.setCurrentIndex(-1)
        self.combo_set.currentIndexChanged.connect(self.set_selected)

        self.line_tape = QtGui.QLineEdit()
        self.grid.addWidget(self.line_tape, 5, 1, 1, 2)

        self.setLayout(self.grid)


    def tape_drive_selected(self):
        dst = str(self.combo_tape_drive.currentText())
        print "Setting tape drive to: " + dst

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
            self.allowed_size = str(file_size_allowed_dict[self.parent.tape_operation_manager.deliverable.media])
            self.label_media_capacity.setText(self.allowed_size)
            self.combo_line.add_dummy_widget()
            self.combo_line.setStyleSheet('background-color: None')
            self.selected_size.clear()
            self.update()

    def sort_file_list(self,file_list,list_items):
        sort_list = []
        sort_dict = {}
        for a_file in file_list:
            linename = a_file.split(".")[0]
            seq_no = int(linename[-3:])
            sort_list.append(seq_no)
            sort_dict.update({seq_no:a_file})
        if list_items == 'all':
            self.file_list = []
            for a_seq in sorted(sort_list):
                self.file_list.append(sort_dict[a_seq])
        elif list_items == 'removed':
            self.file_list_removed = []
            for a_seq in sorted(sort_list):
                self.file_list_removed.append(sort_dict[a_seq])

    def set_selected(self):
        if self.combo_set.currentIndex() == -1:
            pass
        else:
            self.combo_line.setStyleSheet('background-color: None')
            set_no = str(self.combo_set.currentText())
            self.set_no = set_no
            print "Set no is set to: " + str(set_no)
            self.set_selected = True
            self.parent.tape_operation_manager.set_working_set(set_no)
            (file_list,self.file_size_dict) = self.parent.tape_operation_manager.service_class.get_list_of_files_where_ondisk_qc_is_approved()
            file_list_removed = self.parent.tape_operation_manager.service_class.remove_files_written_to_tape(file_list)
            print file_list
            print file_list_removed
            self.sort_file_list(file_list,'all')
            self.sort_file_list(file_list_removed,'removed')
            self.combo_line.toggle_file_selection()
            self.selected_size.clear()
            self.update()


    def reel_no_check(self,tape):
        # This function checks the reel no of all segy selected against reel no entered by the user
        # and issues a warning if the reel no does not match
        status = True
        bad_reel_no_dict = {}
        for a_file in self.segy_to_write_list:
            sgyt_reel_no = self.parent.tape_operation_manager.service_class.approved_obj_dict[a_file].sgyt_reel_no
            if str(sgyt_reel_no) != str(tape):
                status = False
                bad_reel_no_dict.update({a_file : sgyt_reel_no})
        if status == False:
            message_for_pop_up = self.create_message_string_from_incorrect_reel(bad_reel_no_dict,tape)
            overwrite_status = change_log_creation(gui = self, conn_obj=self.parent.tape_operation_manager.db_connection_obj,message=message_for_pop_up,type_entry='change',location='segy_write')
            return overwrite_status
        else:
            return True

    def create_message_string_from_incorrect_reel(self,bad_reel_dict,tape):
        message = 'The reel no entered by user => ' + tape + '\n does not match reel no in EBCDIC for : \n'
        for a_key, value in bad_reel_dict.iteritems():
            message = message +  'EBCDIC reel no for : ' + a_key + ' => ' + value + "\n"
        message = message + "\n please eneter the reson for change log to proceed ."
        return message

    def execute(self):
        self.combo_list = [
            self.combo_tape_drive,
            self.combo_deliverable,
            self.combo_set,
        ]
        combo_entry_check = True
        for a_combo in self.combo_list:
            if a_combo.currentIndex() == -1:
                combo_entry_check = False
                print str(a_combo.objectName()) + " : Is blank aborting"

        if self.file_selected == False:
            print "No file is selected to be written to tape yet !!"
        else:
            if combo_entry_check == True:
                dst = str(self.combo_tape_drive.currentText())
                self.parent.tape_operation_manager.set_tape_drive(dst)
                deliverable = str(self.combo_deliverable.currentText())
                self.parent.tape_operation_manager.set_deliverable(deliverable)
                self.parent.tape_operation_manager.service_class.get_list_of_files_where_ondisk_qc_is_approved()
                file_list = self.segy_to_write_list
                set_no = str(self.combo_set.currentText())
                self.parent.tape_operation_manager.set_working_set(set_no)
                tape = str(self.line_tape.text())
                # This step checks if the reel_no in the db for all files to be wrriten to tape matches the reel_no entered by the user
                if self.reel_no_check(tape):
                    self.parent.SEGY_write_execute(tape, file_list)
                    self.close()



class file_selection(QtGui.QWidget):

    def __init__(self,parent):
        super(file_selection,self).__init__()
        self.parent = parent

        self.grid = QtGui.QGridLayout()

        self.parent.file_selected = False

        self.pb_ok = QtGui.QPushButton('Confirm selection')
        self.pb_ok.clicked.connect(self.ok_exit)
        self.grid.addWidget(self.pb_ok, 0, 0)

        self.ck_box_remove = QtGui.QCheckBox('Remove files already written')
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
        self.parent.selected_size.clear()
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
                    self.check_size_and_exit(return_list)
            else:
                self.check_size_and_exit(return_list)


    def check_size_and_exit(self,return_list):
        self.calculate_combined_file_size(return_list)
        if self.file_size > self.parent.allowed_size:
            warning_message = "The combined file size for the selection is greater than media capacity!!"
            self.warning_pop_up = pop_up_message_box(warning_message, 'Critical')
            self.warning_pop_up.show()
        else:
            print return_list
            self.setStyleSheet('background-color: green')
            self.parent.selected_size.setText(str(self.file_size))
            self.parent.file_selected = True
            self.parent.segy_to_write_list = return_list



class all_files_widget(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()
    def __init__(self,parent):
        super(all_files_widget, self).__init__()
        self.parent = parent
        self.grid = QtGui.QGridLayout()
        self.widget  = QtGui.QWidget()
        i = 0
        self.parent.combo_line.btn_list = []
        for a_file in self.parent.file_list:
            btn = QtGui.QCheckBox(str(a_file + " : " + str(self.parent.file_size_dict[a_file])))
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
        for a_file in self.parent.file_list_removed:
            btn = QtGui.QCheckBox(str(a_file + " : " + str(self.parent.file_size_dict[a_file])))
            btn.setObjectName(a_file)
            self.grid.addWidget(btn, i, 0)
            self.parent.combo_line.btn_list.append(btn)
            i = i + 1
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)

