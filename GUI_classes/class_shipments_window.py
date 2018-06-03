from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels
from class_popup_checkable_combobox import pop_up_check_combo_box_media_association
from class_pop_up_combo_box import pop_up_combo_box
from database_engine.DB_ops import fetch_shipment_objects_list
from database_engine.DB_ops import fetch_deliverable_objects_list
from database_engine.DB_ops import fetch_media_list_did_set

class shipment_tools(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(shipment_tools, self).__init__()
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid = QtGui.QGridLayout()

        grid.addWidget(create_central_labels("Shipments Tools"), 0, 0)

        self.pb_add_shipment = QtGui.QPushButton('Add a new shipment')
        self.pb_add_shipment.setStatusTip('Add a new shipment')
        self.pb_add_shipment.clicked.connect(self.parent.set_add_shipment)
        self.pb_add_shipment.resize(self.pb_add_shipment.minimumSizeHint())


        self.pb_shipment_summary = QtGui.QPushButton("Shipment summary")
        self.pb_shipment_summary.setStatusTip('Shipments summary')
        self.pb_shipment_summary.clicked.connect(
            self.parent.set_shipments_summary)
        self.pb_shipment_summary.resize(self.pb_shipment_summary.minimumSizeHint())


        self.pb_add_media_to_shipment = QtGui.QPushButton("Associate Media with existing shipments")
        self.pb_add_media_to_shipment.setStatusTip('Shipments summary')
        self.pb_add_media_to_shipment.clicked.connect(
            self.associate_media_with_shipment)
        self.pb_add_media_to_shipment.resize(self.pb_add_media_to_shipment.minimumSizeHint())


        grid.addWidget(self.pb_add_shipment,1,0)
        grid.addWidget(self.pb_shipment_summary,2,0)
        grid.addWidget(self.pb_add_media_to_shipment,3,0)

        for i in range(4,16):
            grid.addWidget(QtGui.QLabel(""),i,0)


        self.setLayout(grid)

        self.show()


    def tool_welcome(self):
        print "this tool will be available soon ..."


    def associate_media_with_shipment(self):
        shipment_dao_list = fetch_shipment_objects_list(self.db_connection_obj)
        #Now creating the combo item list
        combo_list = []
        self.shipment_dict = {}
        for dao_obj in shipment_dao_list:
            combo_list.append(dao_obj.number)
            key = dao_obj.number
            data = dao_obj
            self.shipment_dict.update({key:data})
        self.pop_up_combo_box = pop_up_combo_box(self, "Select Shipment", combo_list, 'shipment', 'media_to_shipment')
        self.pop_up_combo_box.closed.connect(self.show)
        self.pop_up_combo_box.show()


    def choose_box_number(self,ops):
        no_boxes = int(self.shipment_dict[self.shipment_no].no_boxes)
        combo_list = []
        for box_no in range(1,no_boxes+1):
            combo_list.append(str(box_no))
        self.pop_up_combo_box = pop_up_combo_box(self, "Select Box number", combo_list, 'box', ops)
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

    def choose_media(self):
        available_media_list = fetch_media_list_did_set(self.db_connection_obj,self.deliverable.id, self.set_no)
        # for item in available_media_list:
        #     print item.media_label
        self.pop_up_combo_box = pop_up_check_combo_box_media_association(self, "Select Media", available_media_list, (self.shipment_no,self.box_no), (self.deliverable, self.set_no))
        self.pop_up_combo_box.show()



    def set_attribute(self, attribute, caller, ops):
        if ops == 'media_to_shipment':
            if caller == 'shipment':
                self.shipment_no = attribute
                self.choose_box_number(ops)
            elif caller =='box':
                self.box_no = attribute
                self.choose_deliverable(ops)
            elif caller == 'deliverable':
                self.deliverable = self.disp_name_dict[attribute]
                self.choose_set_no(ops)
            elif caller == 'set_no':
                self.set_no = attribute
                self.choose_media()










