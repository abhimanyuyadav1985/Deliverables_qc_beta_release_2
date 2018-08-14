from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels
from class_pop_up_message_box import pop_up_message_box

class pop_up_combo_box(QtGui.QWidget):

    closed = QtCore.pyqtSignal()

    def __init__(self, parent, title, list,caller,fn):
        # define the top window

        super(pop_up_combo_box, self).__init__()

        self.parent = parent
        self.caller = caller
        self.fn = fn

        self.grid = QtGui.QGridLayout()
        self.setWindowTitle(title)
        self.combo = QtGui.QComboBox()
        self.combo.addItems(list)

        self.grid.addWidget(create_central_labels(title),0,0)
        self.grid.addWidget(self.combo,0,1)

        self.pb_ok = QtGui.QPushButton('ok')
        self.pb_ok.clicked.connect(self.ok_exit)

        self.grid.addWidget(self.pb_ok,1,0)

        self.setLayout(self.grid)
        self.show()


    def ok_exit(self):
        self.parent.set_attribute(str(self.combo.currentText()),self.caller,self.fn)
        self.close()


class file_selection(QtGui.QWidget):

    def __init__(self,parent, title, list, caller, fn):
        super(file_selection,self).__init__()
        self.parent = parent
        self.file_list = list
        self.grid = QtGui.QGridLayout()
        self.caller = caller
        self.fn = fn
        self.parent.file_selected = False

        self.pb_ok = QtGui.QPushButton('Confirm selection')
        self.pb_ok.clicked.connect(self.ok_exit)
        self.grid.addWidget(self.pb_ok, 0, 0)

        self.grid.addWidget(create_central_labels("Files"), 1, 0)

        self.setLayout(self.grid)

        self.working_widget = all_files_widget(self)
        self.grid.addWidget(self.working_widget, 2, 0)

        self.show()


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
            self.parent.set_attribute(return_list, self.caller, self.fn)
            self.close()


class all_files_widget(QtGui.QScrollArea):
    closed = QtCore.pyqtSignal()
    def __init__(self,parent):
        super(all_files_widget, self).__init__()
        self.parent = parent
        self.grid = QtGui.QGridLayout()
        self.widget  = QtGui.QWidget()
        i = 0
        self.parent.btn_list = []
        for a_file in self.parent.file_list:
            btn = QtGui.QCheckBox(a_file)
            btn.setObjectName(a_file)
            self.grid.addWidget(btn, i, 0)
            self.parent.btn_list.append(btn)
            i = i + 1
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)


