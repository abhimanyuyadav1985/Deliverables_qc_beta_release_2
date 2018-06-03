from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,create_center_data,create_center_blank
from database_engine.DB_ops import add_shipment

class add_new_shipment(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(add_new_shipment, self).__init__(parent=parent)

        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj


        grid =  QtGui.QGridLayout()

        grid.addWidget(create_central_labels("Create New shipment"),0,0,1,3)

        keys_list = ['Id', 'Shipment Number', 'Air way bill number',"Number of boxes"]

        keys_dict = {}
        keys_dict['Id'] = create_center_data('Automatic')
        keys_dict['Shipment Number'] = QtGui.QLineEdit()
        keys_dict['Air way bill number'] = QtGui.QLineEdit()
        keys_dict["Number of boxes"] = QtGui.QLineEdit()

        self.shipment_def = keys_dict

        for i in range(0,len(keys_list)):
            grid.addWidget(create_center_data(keys_list[i]),i+1,0)
            grid.addWidget(keys_dict[keys_list[i]],i+1,1,1,2)


        for i in range (len(keys_list),15):
            grid.addWidget(create_center_blank(""),i+1,1)


        self.pb_save = QtGui.QPushButton()
        self.pb_save.setText('Save')
        self.pb_save.setStatusTip('Save Shipment to the database')
        self.pb_save.clicked.connect(self.save_shipment)

        grid.addWidget(self.pb_save, 17, 0)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Back')
        self.pb_exit.setStatusTip('Back to main Shipment Menu')
        self.pb_exit.clicked.connect(self.parent.set_shipment_tools)

        grid.addWidget(self.pb_exit, 17, 1)

        self.setLayout(grid)

    def save_shipment(self):
        print "Now converting the GUI object to DAO....",
        new_shipment = self.adaptar_gui_to_object()
        print "Done .....now saving it........"
        add_shipment(self.db_connection_obj, new_shipment)
        print "done .... "
        # ---------------------------------------------------------------
        self.parent.set_shipments_summary()

    def adaptar_gui_to_object(self):
        new_shipment = self.db_connection_obj.Shipments()
        new_shipment.number = str(self.shipment_def['Shipment Number'].text())
        new_shipment.awb_no= str(self.shipment_def['Air way bill number'].text())
        new_shipment.no_boxes = str(self.shipment_def['Number of boxes'].text())
        return new_shipment


class edit_shipment(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent,id):
        # define the top window

        super(edit_shipment, self).__init__(parent=parent)
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        grid = QtGui.QGridLayout()

        self.new_shipment = self.db_connection_obj.sess.query(self.db_connection_obj.Shipments).filter(
            self.db_connection_obj.Shipments.id == id).first()

        self.result = self.new_shipment.__dict__

        keys_list = ['Id', 'Shipment Number', 'Air way bill number', "Number of boxes"]
        keys_dict = {}
        keys_dict['Id'] = create_center_data('Automatic')
        keys_dict['Shipment Number'] = QtGui.QLineEdit()
        keys_dict['Air way bill number'] = QtGui.QLineEdit()
        keys_dict["Number of boxes"] = QtGui.QLineEdit()

        self.shipment_def = keys_dict

        for i in range(0, len(keys_list)):
            grid.addWidget(create_center_data(keys_list[i]), i + 1, 0)
            grid.addWidget(keys_dict[keys_list[i]], i + 1, 1, 1, 2)

        for i in range(len(keys_list), 22):
            grid.addWidget(create_center_blank(""), i + 1, 1)


        j = len(keys_list)

        self.pb_save = QtGui.QPushButton()
        self.pb_save.setText('Update')
        self.pb_save.setStatusTip('Save Shipment to the database')
        self.pb_save.clicked.connect(self.update_shipment)

        grid.addWidget(self.pb_save, j + 1, 0)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Back')
        self.pb_exit.setStatusTip('Back to main deliverables Menu')
        self.pb_exit.clicked.connect(self.parent.set_shipments_summary)

        grid.addWidget(self.pb_exit, j + 2, 0)

        self.object_to_gui()

        self.setLayout(grid)

        self.show()

    def update_shipment(self):
        print "Now converting the GUI object to DAO....",
        self.adaptar_gui_to_object()
        self.db_connection_obj.sess.commit()
        self.parent.set_shipments_summary()

    def object_to_gui(self):
        self.shipment_def['Shipment Number'].setText(str(self.result['number']))
        self.shipment_def['Air way bill number'].setText(str(self.result['awb_no']))
        self.shipment_def['Number of boxes'].setText(str(self.result['no_boxes']))


    def adaptar_gui_to_object(self):
        self.new_shipment.number = str(self.shipment_def['Shipment Number'].text())
        self.new_shipment.awb_no = str(self.shipment_def['Air way bill number'].text())
        self.new_shipment.no_boxes = str(self.shipment_def['Number of boxes'].text())


