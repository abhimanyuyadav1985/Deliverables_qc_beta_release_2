from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels

class pop_up_message_box(QtGui.QWidget):

    closed = QtCore.pyqtSignal()

    def __init__(self,message,type):
        # define the top window

        super(pop_up_message_box, self).__init__()
        grid = QtGui.QGridLayout()

        msg = QtGui.QMessageBox()
        msg.setWindowTitle("")
        if type == "Warning":
            msg.setIcon(QtGui.QMessageBox.Warning)
        elif type == "Critical":
            msg.setIcon(QtGui.QMessageBox.Critical)

        msg.setText(message)
        # msg.setInformativeText("This is additional information")
        # msg.setWindowTitle("MessageBox demo")
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.buttonClicked.connect(self.ok_exit)
        grid.addWidget(msg,0,0)
        self.setLayout(grid)


    def ok_exit(self):
        self.closed.emit()
        self.close()


class popup_incorrect_choice_message(QtGui.QWidget):

    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(popup_incorrect_choice_message, self).__init__()


        grid = QtGui.QGridLayout()

        msg = QtGui.QMessageBox()
        msg.setWindowTitle("")

        msg.setIcon(QtGui.QMessageBox.Critical)

        msg.setText("You have typed an incorrect choice!!")
        # msg.setInformativeText("This is additional information")
        # msg.setWindowTitle("MessageBox demo")
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtGui.QMessageBox.Ok)
        msg.buttonClicked.connect(self.ok_exit)
        grid.addWidget(msg,0,0)
        self.setLayout(grid)


    def ok_exit(self):
        self.close()


class pop_up_approval_box(QtGui.QWidget):

    closed = QtCore.pyqtSignal(str,bool)

    def __init__(self,message):
        # define the top window

        super(pop_up_approval_box, self).__init__()


        grid = QtGui.QGridLayout()

        pb_approve = QtGui.QPushButton("Approve")
        pb_approve.setObjectName("Approve")
        pb_approve.clicked.connect(self.ok_exit)

        pb_reject = QtGui.QPushButton("Reject")
        pb_reject.setObjectName("Reject")
        pb_reject.clicked.connect(self.ok_exit)

        message_label = QtGui.QLabel(message)
        grid.addWidget(message_label,0,0,1,2)

        grid.addWidget(QtGui.QLabel('Name'),1,0)
        self.username = QtGui.QLineEdit()
        grid.addWidget(self.username,1,1)
        grid.addWidget(pb_approve,2,0)
        grid.addWidget(pb_reject,2,1)
        self.setLayout(grid)

    def ok_exit(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        name_to_return = str(self.username.text())
        if len(name_to_return) != 0:
            if obj_name == "Approve":
                self.closed.emit(name_to_return,True)
            else:
                self.closed.emit(name_to_return,False)
            self.close()
        else:
            message = "Cannot continue without username !!!1"
            self.pop_up_message_box = pop_up_message_box(self,message,'Critical')


class pop_up_approval_box_segy_write(QtGui.QWidget):

    closed = QtCore.pyqtSignal(str,bool)
    approve_all = QtCore.pyqtSignal(str,bool)

    def __init__(self,message):
        # define the top window

        super(pop_up_approval_box_segy_write, self).__init__()


        grid = QtGui.QGridLayout()

        self.setWindowTitle('SEGY Write log')

        pb_approve = QtGui.QPushButton("Approve")
        pb_approve.setObjectName("Approve")
        pb_approve.clicked.connect(self.ok_exit)

        pb_approve_all = QtGui.QPushButton("Approve all on Tape")
        pb_approve_all.setObjectName("Approve_all")
        pb_approve_all.clicked.connect(self.ok_exit)

        pb_reject = QtGui.QPushButton("Reject")
        pb_reject.setObjectName("Reject")
        pb_reject.clicked.connect(self.ok_exit)

        message_label = QtGui.QTextEdit()
        message_label.setText(message)
        grid.addWidget(message_label,0,0,1,3)

        grid.addWidget(create_central_labels("User Name"),1,0)
        self.username = QtGui.QLineEdit()
        grid.addWidget(self.username,1,1,1,2)
        grid.addWidget(pb_approve,2,1)
        grid.addWidget(pb_approve_all,2,2)
        grid.addWidget(pb_reject,2,0)
        self.setLayout(grid)

    def ok_exit(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        name_to_return = str(self.username.text())
        if len(name_to_return) != 0:
            if obj_name == "Approve":
                self.closed.emit(name_to_return,True)
            elif obj_name == "Approve_all":
                self.approve_all.emit(name_to_return,True)
            else:
                self.closed.emit(name_to_return,False)
            self.close()
        else:
            message = "Cannot continue without username !!!1"
            self.pop_up_message_box = pop_up_message_box(self,message,'Critical')