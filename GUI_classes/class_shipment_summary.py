from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,create_center_data,create_center_blank
from database_engine.DB_ops import fetch_shipments_list, delete_shipment_obj,fetch_deliverable_objects_list
from general_functions.general_functions import change_log_creation
from database_engine.DB_ops import fetch_shipment_objects_list,return_shipment_content_from_number,fetch_project_info
from class_pop_up_combo_box import pop_up_combo_box
import datetime
import os
from configuration import Report_dir
from class_pop_up_text_box import pop_up_text_box_view_only

class shipment_summary(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(shipment_summary, self).__init__()
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid =  QtGui.QGridLayout()

        grid.addWidget(create_central_labels("Shipments Summary"),0,0,1,4)

        labels_text = ["Id", "shipment # ", "AWB #"]
        labels_list = []
        for label in labels_text:
            labels_list.append(create_central_labels(label))
        for i in range(0, len(labels_list)-1):
            grid.addWidget(labels_list[i], 1, i)

        grid.addWidget(labels_list[2],1,2,1,2)
        # ----------------------------------------------------------------------------------
        #  **** Now searcing for existing shipments in the database and displaying them
        # ----------------------------------------------------------------------------------
        self.existing_shipment_list_dict = fetch_shipments_list(self.db_connection_obj)

        sobj = self.existing_shipment_list_dict

        for j in range(0, len(sobj)):
            grid.addWidget(create_center_data(str(sobj[j]['id'])), j + 2, 0)
            grid.addWidget(create_center_data(str(sobj[j]['number'])), j + 2, 1)
            grid.addWidget(create_center_data(str(sobj[j]['awb_no'])), j + 2, 2,1,2)

        # Make it look organized------------------------------------------------
        for j in range(len(sobj), 22):
            for i in range(0, 3):
                grid.addWidget(create_center_blank(""), j + 1, i)
        # ----------------------------------------------------------
        # Adding the button to add deliverable, edit existing one or delete
        # ----------------------------------------------------------
        j = 21

        self.pb_add = QtGui.QPushButton()
        self.pb_add.setText("+")
        self.pb_add.setStatusTip('Add more shipments')
        self.pb_add.clicked.connect(self.parent.set_add_shipment)
        grid.addWidget(self.pb_add, j, 0)

        self.pb_edit = QtGui.QPushButton()
        self.pb_edit.setText('Edit')
        self.pb_edit.setStatusTip('Edit and existing deliverable')
        self.pb_edit.clicked.connect(self.edit_single_shipment)
        grid.addWidget(self.pb_edit, j, 1)

        self.pb_delete = QtGui.QPushButton()
        self.pb_delete.setText('Delete')
        self.pb_delete.setStatusTip('Delete an existing deliverable')
        self.pb_delete.clicked.connect(self.delete_shipment)
        grid.addWidget(self.pb_delete, j, 2)

        self.pb_home = QtGui.QPushButton()
        self.pb_home.setText('Exit')
        self.pb_home.setStatusTip('Exit and return to Home screen ')
        self.pb_home.clicked.connect(self.parent.show_project_info)
        grid.addWidget(self.pb_home, j, 3)

        self.pb_report = QtGui.QPushButton()
        self.pb_report.setText('Content report')
        self.pb_report.setStatusTip('Show shipment content report')
        self.pb_report.clicked.connect(self.shipment_content_report)
        grid.addWidget(self.pb_report, j+1, 0,1,4)


        self.setLayout(grid)

    def delete_shipment(self):
        id, ok = QtGui.QInputDialog.getText(self, "Select the Shipment to delete", "Enter Shipment id:")
        if ok:
            message = str("Please enter the reason to delete the shipment id: " + id)
            perform = change_log_creation(gui = self, conn_obj=self.db_connection_obj,message = message, type_entry="delete", location="shipment_entries")
            if perform:
                print "Now deleting the shipment :: " + str(id)
                delete_shipment_obj(self.db_connection_obj, str(id))
                print "Done ..... "
        self.parent.set_shipments_summary()

    def edit_single_shipment(self):
        id, ok = QtGui.QInputDialog.getText(self, "Select the Shipment to Edit", "Enter Shipment id:")
        if ok:
            message = str("Please enter the reason to change the shipment id: " + id)
            perform = change_log_creation(gui=self, conn_obj=self.db_connection_obj, message=message,
                                          type_entry="change", location="shipment_entries")
            if perform:
                print "Now showing the Shipment :: " + str(id)
                self.parent.set_edit_shipment(str(id))
                print "Done ..... "


    def tool_welcome(self):
        print "This feature will be available shortly ...."


    def shipment_content_report(self):
        shipment_list = fetch_shipment_objects_list(self.db_connection_obj)
        combo_list = []
        for shipment in shipment_list:
            combo_list.append(shipment.number)
        self.pop_up_combo_box = pop_up_combo_box(self,"Choose shipment",combo_list,"ch_shipment","shipment_report")
        self.pop_up_combo_box.closed.connect(self.show)
        self.pop_up_combo_box.show()

    def print_shipment_report(self):
        #1 get list of the shipments with the shipment number as per the choice
        obj_list = return_shipment_content_from_number(self.db_connection_obj,self.shipment_no)
        # 2 get all the deliverables to get the name and media type field
        deliverables_list = fetch_deliverable_objects_list(self.db_connection_obj)
        deliverables_dict = {}
        for deliverable in deliverables_list:
            key = deliverable.id
            data = deliverable
            deliverables_dict.update({key:data})
        # 3 create the file name for the report
        file_name = str(str(datetime.datetime.now().strftime ("%Y%m%d")) + "_" + self.shipment_no+ ".report")
        #4 create the file path
        file_path = os.path.join(os.getcwd(),Report_dir,file_name)
        # 5 now open the file to print the shipment report
        file_out = open(file_path, 'wb')
        #6 Fetch the header information
        self.project_info = fetch_project_info(self.db_connection_obj)
        #Now create the header to be printed to the report
        info_dict = self.project_info[0].__dict__
        hdr = []
        hdr.append("                                  Shipment content Report")
        hdr.append("")
        hdr.append('Polarcus Project ID: ' + info_dict["project"])
        hdr.append('Client Project ID: ' + info_dict['client_project_id'])
        hdr.append('Area:   ' + info_dict["area"])
        hdr.append("Shipment number: " + self.shipment_no)
        #Now print the header to the file
        for i in range(0, len(hdr)):
            print >> file_out, hdr[i]

        print_str_header = '{:>15} {:>3} {:>3} {:>10} {:>8} {:>10}'.format("Deliverable name", "Set", "Box", "Media_Label", "Reel  ","Media Type")
        print_str_blank = " " * len(print_str_header)
        print_str_dash = "-" * len(print_str_header)

        print >> file_out, print_str_blank
        print >> file_out, print_str_dash
        print >> file_out, print_str_header
        print >> file_out, print_str_dash
        for obj in obj_list:
            deliverable = deliverables_dict[obj.deliverable_id]
            print_string = '{:>15} {:>3} {:>3} {:>10} {:>8} {:>10}'.format(deliverable.name,obj.set_no,obj.box_no,obj.media_label,obj.reel_no,deliverable.media)
            print >> file_out, print_string
        print >> file_out, print_str_dash
        file_out.close()

        # open the report in the pop up text box as well so that the user can read it

        file_handler = open(file_path,'rb')
        text_to_append = file_handler.read()
        title = str("Shipment report : " + file_name)
        self.pop_up_text_box = pop_up_text_box_view_only(text = text_to_append, title = title)
        self.pop_up_text_box.closed.connect(self.show)
        self.pop_up_text_box.resize(800, 1000)
        self.pop_up_text_box.show()

    def set_attribute(self,attribute,caller,ops):
        if ops =="shipment_report":
            if caller == 'ch_shipment':
                self.shipment_no = attribute
                self.print_shipment_report()
