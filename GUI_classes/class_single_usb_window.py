from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,create_center_blank,create_center_data
from database_engine.DB_ops import add_usb_list_obj
from database_engine.DB_ops import check_usb_list_obj
from class_pop_up_message_box import pop_up_message_box


class add_usb_label(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(add_usb_label, self).__init__()

        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid = QtGui.QGridLayout()

        grid.addWidget(create_central_labels("Create New USB label"), 0, 0, 1, 3)

        keys_list = ['Id', 'Label', 'Capacity in TB', "Serial no"]

        keys_dict = {}
        keys_dict['Id'] = create_center_data('Automatic')
        keys_dict['Label'] = QtGui.QLineEdit()
        keys_dict['Capacity in TB'] = QtGui.QLineEdit()
        keys_dict['Serial no'] = QtGui.QLineEdit()

        self.usb_def = keys_dict

        for i in range(0, len(keys_list)):
            grid.addWidget(create_center_data(keys_list[i]), i + 1, 0)
            grid.addWidget(keys_dict[keys_list[i]], i + 1, 1, 1, 2)

        for i in range(len(keys_list), 15):
            grid.addWidget(create_center_blank(""), i + 1, 1)

        self.pb_save = QtGui.QPushButton()
        self.pb_save.setText('Save')
        self.pb_save.setStatusTip('Save USB label to database')
        self.pb_save.clicked.connect(self.save_usb_label)

        grid.addWidget(self.pb_save, 17, 0)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Back')
        self.pb_exit.setStatusTip('Back to main Shipment Menu')
        self.pb_exit.clicked.connect(self.parent.set_usb_functions)

        grid.addWidget(self.pb_exit, 17, 1)

        self.setLayout(grid)

    def save_usb_label(self):
        # check is a USB with the same name exists
        result = check_usb_list_obj(self.db_connection_obj,str(self.usb_def['Label'].text()))
        if result == None:
            print "Now converting the GUI object to DAO....",
            new_usb_label = self.adaptar_gui_to_object()
            print "Done .....now saving it........"
            add_usb_list_obj(self.db_connection_obj, new_usb_label)
            print "done .... "
            self.parent.set_usb_summary()
        else:
            message = str("This label already exisits in database, please use a new Label")
            type = "Critical"
            self.pop_up_message_box = pop_up_message_box(self, message,type)
            self.pop_up_message_box.closed.connect(self.show)
            self.pop_up_message_box.show()


    def adaptar_gui_to_object(self):
        new_usb_label = self.db_connection_obj.USB_list()
        new_usb_label.label = str(self.usb_def['Label'].text())
        new_usb_label.capacity_tb = str(self.usb_def['Capacity in TB'].text())
        new_usb_label.serial_no = str(self.usb_def['Serial no'].text())

        return new_usb_label



class edit_usb_window(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent,id):
        # define the top window

        super(edit_usb_window, self).__init__(parent=parent)
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid = QtGui.QGridLayout()

        self.new_usb = self.db_connection_obj.sess.query(self.db_connection_obj.USB_list).filter(
            self.db_connection_obj.USB_list.usb_id == id).first()

        self.result = self.new_usb.__dict__

        keys_list = ['Id', 'Label', 'Capacity in TB', "Serial no"]

        keys_dict = {}
        keys_dict['Id'] = create_center_data('Automatic')
        keys_dict['Label'] = QtGui.QLineEdit()
        keys_dict['Capacity in TB'] = QtGui.QLineEdit()
        keys_dict['Serial no'] = QtGui.QLineEdit()

        self.usb_def = keys_dict

        for i in range(0, len(keys_list)):
            grid.addWidget(create_center_data(keys_list[i]), i + 1, 0)
            grid.addWidget(keys_dict[keys_list[i]], i + 1, 1, 1, 2)

        for i in range(len(keys_list), 15):
            grid.addWidget(create_center_blank(""), i + 1, 1)

        j = len(keys_list)

        self.pb_save = QtGui.QPushButton()
        self.pb_save.setText('Update')
        self.pb_save.setStatusTip('Save USB to the database')
        self.pb_save.clicked.connect(self.update_usb)

        grid.addWidget(self.pb_save, j + 1, 0)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Back')
        self.pb_exit.setStatusTip('Back to main USB Menu')
        self.pb_exit.clicked.connect(self.parent.set_usb_summary)

        grid.addWidget(self.pb_exit, j + 2, 0)

        self.object_to_gui()

        self.setLayout(grid)

        self.show()

    def update_usb(self):
        print "Now converting the GUI object to DAO....",
        self.adaptar_gui_to_object()
        self.db_connection_obj.sess.commit()
        self.parent.set_usb_summary()

    def object_to_gui(self):
        self.usb_def['Label'].setText(str(self.result['label']))
        self.usb_def['Capacity in TB'].setText(str(self.result['capacity_tb']))
        self.usb_def['Serial no'].setText(str(self.result['serial_no']))


    def adaptar_gui_to_object(self):
        self.new_usb.label = str(self.usb_def['Label'].text())
        self.new_usb.capacity_tb = str(self.usb_def['Capacity in TB'].text())
        self.new_usb.serial_no = str(self.usb_def['Serial no'].text())




