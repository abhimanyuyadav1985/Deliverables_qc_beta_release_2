from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels, create_center_data, create_center_blank
from database_engine.DB_ops import fetch_deliverables_list,delete_deliverable_obj
from general_functions.general_functions import change_log_creation
from configuration.Tool_tips import tool_tips_mapper_dict

class Deliverables_summary_window(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(Deliverables_summary_window, self).__init__(parent=parent)
        self.parent = parent
        self.tool_tip_dict = tool_tips_mapper_dict['deliverables']
        self.setToolTip(self.tool_tip_dict['general'])
        self.db_connection_obj = self.parent.db_connection_obj # use this line to pass the connection object between the parent and the child
        grid = QtGui.QGridLayout()
        #header
        title = create_central_labels('Deliverables sumary')
        title.setMaximumHeight(50)
        grid.addWidget(title,0,0,1,6)

        #---------------------------------------------
        #  **creating the label for the widget table
        #---------------------------------------------
        labels_text = ["Id", "Name", "Class", "Type", "Media", "Copies"]
        labels_list = []
        for label in labels_text:
            labels_list.append(create_central_labels(label))
        for i in range(0,len(labels_list)):
            grid.addWidget(labels_list[i],1,i)
        #----------------------------------------------------------------------------------
        #  **** Now searcing for existing deliverables in the database and displaying them
        #----------------------------------------------------------------------------------
        self.existing_deliverables_list_dict = fetch_deliverables_list(self.db_connection_obj)
        sobj = self.existing_deliverables_list_dict
        for j in range(0,len(sobj)):
            grid.addWidget(create_center_data(str(sobj[j]['id'])),j+2,0)
            grid.addWidget(create_center_data(str(sobj[j]['name'])),j+2,1)
            grid.addWidget(create_center_data(str(sobj[j]['class_d'])), j + 2, 2)
            grid.addWidget(create_center_data(str(sobj[j]['type'])), j + 2, 3)
            grid.addWidget(create_center_data(str(sobj[j]['media'])), j + 2, 4)
            grid.addWidget(create_center_data(str(sobj[j]['copies'])), j + 2, 5)

        #Make it look organized------------------------------------------------
        for j in range(len(sobj),22):
            for i in range (0,6):
                grid.addWidget(create_center_blank(""),j+1,i)
        #----------------------------------------------------------
        # Adding the button to add deliverable, edit existing one or delete
        #----------------------------------------------------------
        j = 22
        self.pb_add = QtGui.QPushButton()
        self.pb_add.setText("+")
        self.pb_add.clicked.connect(self.parent.set_new_deliverable)
        grid.addWidget(self.pb_add,j,0)
        self.pb_add.setToolTip(self.tool_tip_dict['add'])

        self.pb_edit = QtGui.QPushButton()
        self.pb_edit.setText('Edit')
        self.pb_edit.clicked.connect(self.edit_single_deliverable)
        grid.addWidget(self.pb_edit,j,2)
        self.pb_edit.setToolTip(self.tool_tip_dict['edit'])

        self.pb_view = QtGui.QPushButton()
        self.pb_view.setText('View')
        self.pb_view.clicked.connect(self.view_single_deliverable_detail)
        grid.addWidget(self.pb_view, j, 1)
        self.pb_view.setToolTip(self.tool_tip_dict['view'])

        self.pb_delete = QtGui.QPushButton()
        self.pb_delete.setText('Delete')
        self.pb_delete.clicked.connect(self.delete_deliverable)
        grid.addWidget(self.pb_delete,j,3)
        self.pb_delete.setToolTip(self.tool_tip_dict['delete'])

        self.pb_home = QtGui.QPushButton()
        self.pb_home.setText('Exit')
        self.pb_home.clicked.connect(self.parent.show_project_info)
        grid.addWidget(self.pb_home, j, 5)
        self.pb_home.setToolTip(self.tool_tip_dict['exit'])

        self.setLayout(grid)

    def delete_deliverable(self):
        id, ok = QtGui.QInputDialog.getText(self, "Type the Deliverable id to delete","Enter deliverable id:")
        if ok:
            message = str("Please enter the reason to delete the deliverabe id : " + id)
            perform = change_log_creation(gui=self,conn_obj=self.db_connection_obj,message = message,type_entry="delete",location="deliverables")
            if perform:
                print "now deleting the deliverable :: " + str(id)
                delete_deliverable_obj(self.db_connection_obj,str(id))
                print "Done ..... "
        self.parent.set_deliverables_window()

    def view_single_deliverable_detail(self):
        id, ok = QtGui.QInputDialog.getText(self, "Type the Deliverable id to view", "Enter deliverable id:")
        if ok:
            print "Now showing the deliverable :: " + str(id)
            self.parent.set_view_single_deliverable_detail(str(id))
            print "Done ..... "

    def edit_single_deliverable(self):
        id, ok = QtGui.QInputDialog.getText(self, "Type the Deliverable id to Edit", "Enter deliverable id:")
        if ok:
            path_decide, ok = QtGui.QInputDialog.getText(self, "Is the reason SGYT, bin def or Trc def files ? type y to confrim n for any other reason", "Is the reason SGYT, bin def or Trc def files ? type y to confrim n for any other reason")
            if path_decide == "y":
                print "Now showing the deliverable :: " + str(id)
                self.parent.set_edit_single_deliverable_detail(str(id))
                print "Done ..... "
            elif path_decide =='n':
                message = str("Please enter the reason to change the deliverabe id : " + id)
                perform = change_log_creation(gui=self, conn_obj=self.db_connection_obj, message=message,
                                              type_entry="change", location="deliverables")
                if perform:
                    print "Now showing the deliverable :: " + str(id)
                    self.parent.set_edit_single_deliverable_detail(str(id))
                    print "Done ..... "
        pass


def main():
    display = Deliverables_summary_window

if '__name__' == '__main__':
    main()
