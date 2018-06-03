from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels

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



