from PyQt4 import QtGui, QtCore
from database_engine.DB_ops import get_list_of_segd_deliverables,get_all_available_segd_tapes_in_orca
from database_engine.DB_ops import fetch_seq_name_from_id,get_all_SEGD_qc_entries
from general_functions.general_functions import create_central_labels,create_center_data, decide_and_create_label
from database_engine.DB_ops import return_SEGD_QC_log_path
from dug_ops.DUG_ops import return_encoded_log
from class_pop_up_text_box import pop_up_text_box_view_only
from configuration.Tool_tips import tool_tips_mapper_dict

import time
import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)


class refresh_enabled_SEGD_QC_summary(QtGui.QWidget):
    def __init__(self,parent):
        super(refresh_enabled_SEGD_QC_summary,self).__init__()
        ts = time.time()
        self.parent = parent
        self.grid = QtGui.QGridLayout()
        pb_refresh = QtGui.QPushButton('Refresh')
        pb_refresh.clicked.connect(self.parent.run_SEGD_QC_summary_sync)
        self.grid.addWidget(pb_refresh,0,2,1,1)
        pb_refresh.setMaximumHeight(20)
        self.summary = SEGD_QC_summary(self.parent)
        self.get_applicable_deliverables()
        self.get_total_widget_width()
        self.labels_creation()
        self.summary.create_summary()
        self.grid.addWidget(self.summary,2,0,1,3)
        self.setLayout(self.grid)
        self.show()
        te = time.time()
        time_string = "{:8.5f} sec".format(te - ts)
        logger.info("Finished Creating SEGD QC Summary widget in: " +  time_string)

    def get_applicable_deliverables(self):
        self.deliverables_list = get_list_of_segd_deliverables(self.parent.db_connection_obj)

    def get_total_widget_width(self):
        i = 0
        for deliverable in self.deliverables_list:
            i = i+int(deliverable.copies)*3
        self.total_widget_width = i+2

    def labels_creation(self):
        self.labels_widget = labels_widget_SEGD_QC_summary(self)
        self.grid.addWidget(self.labels_widget,1,0,1,3)

class SEGD_QC_summary(QtGui.QScrollArea):

    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(SEGD_QC_summary, self).__init__()
        self.tool_tip_dict = tool_tips_mapper_dict['segd_status']
        self.setToolTip(self.tool_tip_dict['general'])
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connectioni_obj = self.parent.DUG_connection_obj

    def create_summary(self):
        self.widget = QtGui.QWidget()
        self.grid = QtGui.QGridLayout()
        self.get_applicable_deliverables()
        self.get_total_widget_width()
        self.get_applicable_tapes()
        self.add_tape_sequence_labels()
        self.get_all_SEGD_qc_entries()
        self.add_db_entries_to_table()
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        # self.setMinimumWidth(self.widget.sizeHint().width())
        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def get_applicable_deliverables(self):
        self.deliverables_list = get_list_of_segd_deliverables(self.db_connection_obj)

    def get_total_widget_width(self):
        i = 0
        for deliverable in self.deliverables_list:
            i = i + int(deliverable.copies) * 3
        self.total_widget_width = i + 2

    def add_tape_sequence_labels(self):
        rv_dict = {}  # row values for SEG QC entries
        for i in range(0,len(self.tape_list)):
            seq_name = fetch_seq_name_from_id(self.db_connection_obj,self.tape_list[i].sequence_number)
            self.grid.addWidget(create_center_data(self.tape_list[i].name),i+4,1,1,1)
            self.grid.addWidget(create_center_data(seq_name), i + 4, 0, 1, 1)
            rv_dict.update({self.tape_list[i].name:i+4})
        self.rv_dict = rv_dict

    def get_applicable_tapes(self):
        self.tape_list = get_all_available_segd_tapes_in_orca(self.db_connection_obj)


    def get_all_SEGD_qc_entries(self):
        self.db_segd_qc_entry_list = get_all_SEGD_qc_entries(self.db_connection_obj)


    def add_db_entries_to_table(self):
        db_entry_reference_dict = {}
        db_entry_plot_dict = {}
        for db_entry in self.db_segd_qc_entry_list:
            db_entry_reference_dict.update({(db_entry.tape_no, db_entry.deliverable_id, db_entry.set_no):db_entry})
        for tape in self.tape_list:
            for deliverable in self.deliverables_list:
                for i in range(1,int(deliverable.copies)+1):
                    key = (tape.name,deliverable.id,i)
                    if key in db_entry_reference_dict.keys():
                        pass
                    else:
                        db_entry_reference_dict.update({key: None})
        for key in db_entry_reference_dict.keys():
            if db_entry_reference_dict[key] is not None:

                if str(db_entry_reference_dict[key].run_finish) == 'True':
                    db_entry = db_entry_reference_dict[key]
                    rp = self.rv_dict[db_entry.tape_no]
                    self.grid.addWidget(decide_and_create_label(db_entry.run_status),rp,int(self.cv_dict[db_entry.deliverable_id][db_entry.set_no]['Run']))
                    pb = QtGui.QPushButton(str(db_entry.qc_status))
                    obj_name = str(db_entry.tape_no +"-" +str(db_entry.set_no))
                    pb.setObjectName(obj_name)
                    pb.setToolTip(return_SEGD_QC_log_path(self.db_connection_obj,tape_no = obj_name.split("-")[0],set_no=obj_name.split("-")[1]))
                    pb.clicked.connect(self.show_log)
                    if str(db_entry.qc_status) == "True":
                        pb.setStyleSheet('background-color: green')
                    else:
                        pb.setStyleSheet('background-color: red')

                    self.grid.addWidget(pb,rp,int(self.cv_dict[db_entry.deliverable_id][db_entry.set_no]['QC']))
                    self.grid.addWidget(decide_and_create_label('True'), rp,
                                        int(self.cv_dict[db_entry.deliverable_id][db_entry.set_no]['Prod']))
                else:
                    db_entry = db_entry_reference_dict[key]
                    rp = self.rv_dict[db_entry.tape_no]
                    self.grid.addWidget(decide_and_create_label('True'), rp,
                                        int(self.cv_dict[db_entry.deliverable_id][db_entry.set_no]['Prod']))
                    self.grid.addWidget(decide_and_create_label('Running'), rp,
                                        int(self.cv_dict[db_entry.deliverable_id][db_entry.set_no]['Run']))

            else:
                rp = self.rv_dict[key[0]]
                self.grid.addWidget(decide_and_create_label('Ready'), rp,
                                    int(self.cv_dict[key[1]][key[2]]['Run']))
                self.grid.addWidget(decide_and_create_label('True'), rp,
                                    int(self.cv_dict[key[1]][key[2]]['Prod']))



    def show_log(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        obj_name_list = obj_name.split("-")
        tape_no = obj_name_list[0]
        set_no = obj_name_list[1]
        log_path = return_SEGD_QC_log_path(self.db_connection_obj,tape_no = tape_no,set_no=set_no)
        encoded_string = return_encoded_log(DUG_connection_obj = self.DUG_connectioni_obj,log_path = log_path)
        text_to_show = encoded_string.decode('base64')
        #print text_to_show
        #print text_to_show
        title = str("SEGD QC log for tape no: " + tape_no + " set no: " + set_no)
        self.pop_up_text_box = pop_up_text_box_view_only(text_to_show,title = title)
        self.pop_up_text_box.closed.connect(self.show)
        self.pop_up_text_box.resize(1500, 1000)
        self.pop_up_text_box.show()




class labels_widget_SEGD_QC_summary(QtGui.QWidget):
    def __init__(self,parent):
        super(labels_widget_SEGD_QC_summary,self).__init__()

        self.grid = QtGui.QGridLayout()
        self.parent = parent

        qc_labels_list = ['Prod', 'Run', 'QC']
        self.grid.addWidget(create_central_labels("SEGD QC summary"), 0, 0, 1, self.parent.total_widget_width)
        self.grid.addWidget(create_central_labels("Line name"), 3, 0, 1, 1)
        self.grid.addWidget(create_central_labels("Tape no"), 3, 1, 1, 1)

        start_value_for_deliverable = 2

        cv_dict = {}  # column values for SEGD QC entries

        # structure = {deliverable_id:{set_no:{prod:xx,run:xx,qc:xx}}}

        for deliverable in self.parent.deliverables_list:
            label_text = str(str(deliverable.id) + " " + deliverable.name)
            width = int(deliverable.copies) * 3
            self.grid.addWidget(create_central_labels(label_text), 1, start_value_for_deliverable, 1, width)

            set_start_value = start_value_for_deliverable
            set_dict = {}
            for set in range(1, int(deliverable.copies) + 1):
                label_text = str("Set : " + str(set))
                self.grid.addWidget(create_central_labels(label_text), 2, set_start_value, 1, 3)
                status_dict = {}
                for i in range(0, len(qc_labels_list)):
                    status_dict.update({qc_labels_list[i]: set_start_value + i})
                    self.grid.addWidget(create_central_labels(qc_labels_list[i]), 3, set_start_value + i, 1, 1)

                set_dict.update({set: status_dict})
                set_start_value = set_start_value + 3
            cv_dict.update({deliverable.id: set_dict})
            start_value_for_deliverable = start_value_for_deliverable + width + 1
        self.parent.summary.cv_dict = cv_dict

        self.setLayout(self.grid)

