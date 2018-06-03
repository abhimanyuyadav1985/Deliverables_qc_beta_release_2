from PyQt4 import QtGui, QtCore


class pop_up_text_box_view_only(QtGui.QWidget):

    closed = QtCore.pyqtSignal()

    def __init__(self,text,title):
        # define the top window

        super(pop_up_text_box_view_only, self).__init__()
        grid = QtGui.QGridLayout()
        self.text_edit = QtGui.QTextEdit()

        self.text_edit.setStyleSheet('''
            QTextEdit {
                font: 10pt "Consolas";
            }
        ''')
        self.text_edit.setPlainText(text)
        grid.addWidget(self.text_edit, 0, 0)
        self.setWindowTitle(title)
        self.text_edit.resize(600,800)
        self.setLayout(grid)
        self.show()


    def closeEvent(self, event):
        self.closed.emit()
        event.accept()




class pop_up_text_box_sgyt(QtGui.QWidget):

    closed = QtCore.pyqtSignal()

    def __init__(self,text,title):
        # define the top window

        super(pop_up_text_box_sgyt, self).__init__()
        grid = QtGui.QGridLayout()
        self.text_edit = QtGui.QTextEdit()

        self.text_edit.setStyleSheet('''
            QTextEdit {
                font: 10pt "Consolas";
            }
        ''')
        for a_line in text:
            self.text_edit.append(a_line)
        grid.addWidget(self.text_edit, 0, 0)
        self.setWindowTitle(title)
        self.text_edit.resize(600,800)
        self.setLayout(grid)
        self.show()


    def closeEvent(self, event):
        self.closed.emit()
        event.accept()