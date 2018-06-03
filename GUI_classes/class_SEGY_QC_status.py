from PyQt4 import QtGui,QtCore
from database_engine.DB_ops import get_deliverable_object
from general_functions.general_functions import create_central_labels
from dug_ops.segy_templ import return_ebcdic_from_sgyt,decode_string
from class_pop_up_message_box import pop_up_message_box
from class_pop_up_text_box import pop_up_text_box_view_only
from configuration import sequence_wise_SEGY,SEGY_3D
from class_SEGY_SEQG_tabs import SEQG_SEGY_status_tabs
from class_SEGY_3D_tabs import SEGY_3D_status_tabs
from configuration.Tool_tips import tool_tips_mapper_dict

import logging, time
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class SEGY_qc_status(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()
    def __init__(self,parent,deliverable):

        super(SEGY_qc_status, self).__init__()
        ts = time.time()
        self.tool_tip_dict = tool_tips_mapper_dict['segy_status']
        self.setToolTip(self.tool_tip_dict['general'])

        self.parent = parent
        self.minimum_width = 800
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.deliverable = deliverable
        self.deliverable_id = self.deliverable.id

        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(create_central_labels("Deliverable details"), 0, 0,1,4 )

        self.pb_refresh = QtGui.QPushButton("Refresh")
        self.pb_refresh.clicked.connect(self.refresh)
        self.pb_refresh.setStyleSheet('background-color: yellow')
        self.grid.addWidget(self.pb_refresh,0,4)

        self.deliverable_info_widget = deliverable_info_widget(self)
        self.deliverable_info_widget.setFixedHeight(50)
        self.deliverable_info_widget.setMinimumWidth(self.minimum_width)

        self.grid.addWidget(self.deliverable_info_widget,1,0,1,5)

        self.decide_and_use_type_tabs()

        self.setLayout(self.grid)

        te = time.time()
        time_string = "{:8.5f} sec".format(te - ts)
        logger.info("Finished Creating SEGY Summary widget in: " + time_string)
        #self.show()

    def refresh(self):
        self.parent.set_segy_qc_status(self.deliverable)


    def decide_and_use_type_tabs(self): # This function decided which type of GUI is necessary for a deliverable type for SEGY QC
        if self.deliverable.type in sequence_wise_SEGY:
            self.SEGY_QC_tabs = SEQG_SEGY_status_tabs(self)
            self.SEGY_QC_tabs.setMinimumWidth(self.minimum_width)
        elif self.deliverable.type in SEGY_3D:
            self.SEGY_QC_tabs = SEGY_3D_status_tabs(self)
        self.grid.addWidget(self.SEGY_QC_tabs, 2, 0,1,5)

#-----------------------------------------------------------------------------------------
class deliverable_info_widget(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()
    def __init__(self, parent):
        super(deliverable_info_widget, self).__init__()
        self.parent = parent

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.deliverable_id = self.parent.deliverable_id

        grid = QtGui.QGridLayout()


         #go get the deliverable_object_from the database
        self.deliverable_obj = get_deliverable_object(self.db_connection_obj,self.deliverable_id)

        label_deliverable_name = create_central_labels(str(str(self.deliverable_obj.id) + " : " + self.deliverable_obj.name))
        label_deliverable_media = create_central_labels(str("Media: " + self.deliverable_obj.media))

        pb_sgyt = QtGui.QPushButton('SGYT_EBCDIC')
        pb_bin_def = QtGui.QPushButton('Bin.def')
        pb_trc_def = QtGui.QPushButton('Trc.def')

        grid.addWidget(label_deliverable_name,0,0,1,2)
        grid.addWidget(label_deliverable_media,0,2,1,2)
        grid.addWidget(pb_sgyt,0,4)
        grid.addWidget(pb_bin_def,0,5)
        grid.addWidget(pb_trc_def,0,6)

        if self.deliverable_obj.sgyt_master_status:
            pb_sgyt.clicked.connect(self.show_EBCDIC)
        else:
            pb_sgyt.clicked.connect(self.show_warning_message)


        if self.deliverable_obj.bin_def_status:
            pb_bin_def.clicked.connect(self.show_bin_def)
        else:
            pb_bin_def.clicked.connect(self.show_warning_message)

        if self.deliverable_obj.trc_def_status:
            pb_trc_def.clicked.connect(self.show_trc_def)
        else:
            pb_trc_def.clicked.connect(self.show_warning_message)

        self.setLayout(grid)

        #self.show()


    def show_EBCDIC(self):
        sgyt_string = decode_string(self.deliverable_obj.sgyt)
        ebcdic = return_ebcdic_from_sgyt(sgyt_string)
        title = str(str(self.deliverable_obj.id)) + " " + str(self.deliverable_obj.name) + ' EBCDIC'
        self.ebcdic_text_box = pop_up_text_box_view_only("", title)
        for i in range(0, 3201, 80):
            self.ebcdic_text_box.text_edit.append(ebcdic[i:i + 80])
        self.ebcdic_text_box.closed.connect(self.show)
        self.ebcdic_text_box.resize(800, 700)
        self.ebcdic_text_box.show()

    def show_bin_def(self):
        bin_def = decode_string(self.deliverable_obj.bin_def)
        title = str(str(self.deliverable_obj.id)) + " " + str(self.deliverable_obj.name) + ' Bin.def'
        self.bin_def_text_box = pop_up_text_box_view_only(bin_def, title)
        self.bin_def_text_box.closed.connect(self.show)
        self.bin_def_text_box.resize(700, 600)
        self.bin_def_text_box.show()

    def show_trc_def(self):
        bin_def = decode_string(self.deliverable_obj.trc_def)
        title = str(str(self.deliverable_obj.id)) + " " + str(self.deliverable_obj.name) + ' Trc.def'
        self.trc_def_text_box = pop_up_text_box_view_only(bin_def, title)
        self.trc_def_text_box.closed.connect(self.show)
        self.trc_def_text_box.resize(700, 600)
        self.trc_def_text_box.show()


    def show_warning_message(self):
        self.pop_up_message_box = pop_up_message_box("Not found in DB","Critical")
        self.pop_up_message_box.closed.connect(self.show)
        self.pop_up_message_box.show()
