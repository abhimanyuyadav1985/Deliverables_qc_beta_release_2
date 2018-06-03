from PyQt4 import QtGui, QtCore
from general_functions.general_functions import create_central_labels

class threads_dock(QtGui.QScrollArea):
    def __init__(self, parent):
        # define the top window
        self.parent = parent
        self.thread_dict = self.parent.thread_dict
        super(threads_dock, self).__init__(parent=parent)

        self.grid = QtGui.QGridLayout()


        self.t_1 = QtGui.QTextEdit()
        self.t_2 = QtGui.QTextEdit()
        self.t_3 = QtGui.QTextEdit()
        self.t_4 = QtGui.QTextEdit()


        self.l1 =  QtGui.QLabel("T1")
        self.l1.setStyleSheet('background-color: green ; color : white')
        self.l1.setAlignment(QtCore.Qt.AlignCenter)
        self.l1.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)

        self.l2 = QtGui.QLabel("T2")
        self.l2.setStyleSheet('background-color: green ; color : white')
        self.l2.setAlignment(QtCore.Qt.AlignCenter)
        self.l2.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)

        self.l3 = QtGui.QLabel("T3")
        self.l3.setStyleSheet('background-color: green ; color : white')
        self.l3.setAlignment(QtCore.Qt.AlignCenter)
        self.l3.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)

        self.l4 = QtGui.QLabel("T4")
        self.l4.setStyleSheet('background-color: green ; color : white')
        self.l4.setAlignment(QtCore.Qt.AlignCenter)
        self.l4.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)


        self.grid.addWidget(self.t_1,0,1,1,3)
        self.grid.addWidget(self.t_2, 3, 1,1,3)
        self.grid.addWidget(self.t_3, 6, 1,1,3)
        self.grid.addWidget(self.t_4, 9, 1,1,3)


        self.grid.addWidget(self.l1,0,0,3,1)
        self.grid.addWidget(self.l2, 3,0, 3, 1)
        self.grid.addWidget(self.l3,6, 0, 3,1)
        self.grid.addWidget(self.l4, 9, 0, 3, 1)

        self.t1_s = 0
        self.t2_s = 0
        self.t3_s = 0
        self.t4_s = 0



        self.setLayout(self.grid)
        self.show()


    def thread_control(self,status,print_str,thread_name):
        if thread_name == 'thread1':
            if self.t1_s == 0 and status:
                self.t_1.clear()
                self.t1_s =1
            if status:
                self.t_1.append(print_str)
                self.t1_s = 1
                self.l1.setStyleSheet('background-color: red ; color : white')
                self.grid.addWidget(self.l1, 0, 0, 3, 1)
            else:
                self.t1_s = 0
                self.l1.setStyleSheet('background-color: green ; color : white')
                self.grid.addWidget(self.l1, 0, 0, 3, 1)
        elif thread_name == 'thread2':
            if self.t2_s == 0 and status:
                self.t_2.clear()
                self.t2_s = 1
            if status:
                self.t_2.append(print_str)
                self.t2_s = 1
                self.l2.setStyleSheet('background-color: red ; color : white')
                self.grid.addWidget(self.l2, 3, 0, 3, 1)
            else:
                self.t2_s = 0
                self.l2.setStyleSheet('background-color: green ; color : white')
                self.grid.addWidget(self.l2, 3, 0, 3, 1)
        elif thread_name == 'thread3':
            if self.t3_s == 0 and status:
                self.t_3.clear()
                self.t3_s = 1
            if status:
                self.t_3.append(print_str)
                self.t3_s = 1
                self.l3.setStyleSheet('background-color: red ; color : white')
                self.grid.addWidget(self.l3, 6, 0, 3, 1)
            else:
                self.t3_s = 0
                self.l3.setStyleSheet('background-color: green ; color : white')
                self.grid.addWidget(self.l3, 6, 0, 3, 1)
        elif thread_name == 'thread4':
            if self.t4_s == 0 and status:
                self.t_4.clear()
                self.t4_s = 1
            if status:
                self.t_4.append(print_str)
                self.l4.setStyleSheet('background-color: red ; color : white')
                self.grid.addWidget(self.l4,9, 0, 3, 1)
            else:
                self.t4_s = 0
                self.l4.setStyleSheet('background-color: green ; color : white')
                self.grid.addWidget(self.l4, 9, 0, 3, 1)





