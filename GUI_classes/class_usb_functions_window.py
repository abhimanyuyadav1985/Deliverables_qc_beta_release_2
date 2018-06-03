from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels
from database_engine.DB_ops import get_all_available_usb
from database_engine.DB_ops import fetch_deliverable_objects_list
from class_pop_up_combo_box import pop_up_combo_box
# from class_popup_checkable_combobox import


class usb_tools_window(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(usb_tools_window, self).__init__()

        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid = QtGui.QGridLayout()

        self.pb_add_usb_label = QtGui.QPushButton("Create new USB label")
        self.pb_add_usb_label.clicked.connect(self.parent.set_add_usb_label)

        self.pb_add_media_to_usb_tape = QtGui.QPushButton("Associate files with USB (on Tape as well)")
        self.pb_add_usb_label.clicked.connect(self.associate_files_with_usb_on_tape)

        self.pb_add_media_to_usb_no_tape = QtGui.QPushButton("Associate files with USB (No tape)")
        self.pb_add_usb_label.clicked.connect(self.tool_welcome)


        self.pb_show_usb_summary = QtGui.QPushButton("Show USB summary")
        self.pb_show_usb_summary.clicked.connect(self.parent.set_usb_summary)


        grid.addWidget(create_central_labels("USB tools"),0,0)
        grid.addWidget(self.pb_add_usb_label,1,0)
        grid.addWidget(self.pb_add_media_to_usb_tape,2,0)
        grid.addWidget(self.pb_add_media_to_usb_no_tape, 3, 0)
        grid.addWidget(self.pb_show_usb_summary,4,0)

        for i in range(5,16):
            grid.addWidget(QtGui.QLabel(""),i,0)


        self.setLayout(grid)
        self.show()

    def tool_welcome(self):
        print "This function will be available soon ... "



    def associate_files_with_usb_on_tape(self):
        usb_dao_list = get_all_available_usb(self.db_connection_obj)
        #Now creating the combo item list
        combo_list = []
        self.usb_dict = {}
        for dao_obj in usb_dao_list:
            combo_list.append(dao_obj.label)
            key = dao_obj.label
            data = dao_obj
            self.usb_dict.update({key:data})
        self.pop_up_combo_box = pop_up_combo_box(self, "Select USB", combo_list, 'USB', 'files_to_usb')
        self.pop_up_combo_box.closed.connect(self.show)
        self.pop_up_combo_box.show()



    def choose_deliverable(self,ops):
        deliverables_list = fetch_deliverable_objects_list(self.db_connection_obj)
        disp_name_dict = {}
        combo_item_list = []
        for deliverable in deliverables_list:
            key = str(deliverable.id) + "_" + deliverable.name
            data = deliverable
            disp_name_dict.update({key: data})
            combo_item_list.append(key)
        self.disp_name_dict = disp_name_dict
        self.pop_up_combo_box = pop_up_combo_box(self, "Select deliverable", combo_item_list, 'deliverable', ops)
        self.pop_up_combo_box.show()

    def choose_set_no(self,ops):
        combo_list = []
        for set_no in range(1,int(self.deliverable.copies)+1):
            combo_list.append(str(set_no))
        self.pop_up_combo_box = pop_up_combo_box(self, "Select set number", combo_list, 'set_no', ops)
        self.pop_up_combo_box.show()

    def choose_files(self):
        # available_media_list = fetch_media_list_did_set(self.db_connection_obj,self.deliverable.id, self.set_no)
        # # for item in available_media_list:
        # #     print item.media_label
        # self.pop_up_combo_box = pop_up_check_combo_box_media_association(self, "Select Media", available_media_list, (self.shipment_no,self.box_no), (self.deliverable, self.set_no))
        # self.pop_up_combo_box.show()
        pass



    def set_attribute(self, attribute, caller, ops):
        if ops == 'files_to_usb':
            if caller == 'shipment':
                self.usb_label = attribute
                self.choose_deliverable(ops)
            elif caller == 'deliverable':
                self.deliverable = self.disp_name_dict[attribute]
                self.choose_set_no(ops)
            elif caller == 'set_no':
                self.set_no = attribute
                pass










