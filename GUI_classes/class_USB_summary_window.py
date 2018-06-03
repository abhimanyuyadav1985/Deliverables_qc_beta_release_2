from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,create_center_data,create_center_blank
from database_engine.DB_ops import fetch_usb_list_dict, delete_usb_list_obj
from general_functions.general_functions import change_log_creation

class usb_summary_window(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(usb_summary_window, self).__init__()
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid =  QtGui.QGridLayout()

        grid.addWidget(create_central_labels("USB Summary"),0,0,1,4)

        labels_text = ["Id", "USB # ",  "Capacity" , "Serial #"]
        labels_list = []
        for label in labels_text:
            labels_list.append(create_central_labels(label))
        for i in range(0, len(labels_list)):
            grid.addWidget(labels_list[i], 1, i)

        # ----------------------------------------------------------------------------------
        #  **** Now searcing for existing shipments in the database and displaying them
        # ----------------------------------------------------------------------------------
        self.existing_usb_list_dict = fetch_usb_list_dict(self.db_connection_obj)

        sobj = self.existing_usb_list_dict

        for j in range(0, len(sobj)):
            grid.addWidget(create_center_data(str(sobj[j]['usb_id'])), j + 2, 0)
            grid.addWidget(create_center_data(str(sobj[j]['label'])), j + 2, 1)
            grid.addWidget(create_center_data(str(sobj[j]['capacity_tb'])), j + 2, 2)
            grid.addWidget(create_center_data(str(sobj[j]['serial_no'])), j + 2, 3)


        # Make it look organized------------------------------------------------
        for j in range(len(sobj), 22):
            for i in range(0, 4):
                grid.addWidget(create_center_blank(""), j + 1, i)
        # ----------------------------------------------------------
        # Adding the button to add deliverable, edit existing one or delete
        # ----------------------------------------------------------
        j = 22

        self.pb_add = QtGui.QPushButton()
        self.pb_add.setText("+")
        self.pb_add.setStatusTip('Add more USB')
        self.pb_add.clicked.connect(self.parent.set_add_usb_label)
        grid.addWidget(self.pb_add, j, 0)

        self.pb_edit = QtGui.QPushButton()
        self.pb_edit.setText('Edit')
        self.pb_edit.setStatusTip('Edit and existing USB')
        self.pb_edit.clicked.connect(self.edit_single_usb)
        grid.addWidget(self.pb_edit, j, 1)

        self.pb_delete = QtGui.QPushButton()
        self.pb_delete.setText('Delete')
        self.pb_delete.setStatusTip('Delete an existing USB')
        self.pb_delete.clicked.connect(self.delete_usb)
        grid.addWidget(self.pb_delete, j, 2)

        self.pb_home = QtGui.QPushButton()
        self.pb_home.setText('Exit')
        self.pb_home.setStatusTip('Exit and return to Home screen ')
        self.pb_home.clicked.connect(self.parent.show_project_info)
        grid.addWidget(self.pb_home, j, 3)

        self.setLayout(grid)

    def delete_usb(self):
        id, ok = QtGui.QInputDialog.getText(self, "Select the USB to delete", "Enter USB id:")
        if ok:
            message = str("Please enter the reason to delete the USB id: " + id)
            perform = change_log_creation(gui=self, conn_obj=self.db_connection_obj,message = message, type_entry="delete",location="usb_list")
            if perform:
                print "Now deleting the USB id :: " + str(id)
                delete_usb_list_obj(self.db_connection_obj, str(id))
                print "Done ..... "
        self.parent.set_usb_summary()

    def edit_single_usb(self):
        id, ok = QtGui.QInputDialog.getText(self, "Select the USB to Edit", "Enter USB id:")
        if ok:
            message = str("Please enter the reason to change the USB id: " + id)
            perform = change_log_creation(gui=self, conn_obj=self.db_connection_obj, message=message,
                                          type_entry="change", location="usb_list")
            if perform:
                print "Now showing the USB ID :: " + str(id)
                self.parent.set_edit_usb(str(id))
                print "Done ..... "
        pass



