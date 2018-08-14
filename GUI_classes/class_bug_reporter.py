from PyQt4 import QtGui, QtCore, QtWebKit

class bug_reporter(QtGui.QWidget):
    def __init__(self):
        super(bug_reporter,self).__init__()
        self.setWindowTitle('Support Request form')
        grid = QtGui.QVBoxLayout()
        browser = QtWebKit.QWebView()
        browser.load(QtCore.QUrl('http://10.64.1.21'))
        browser.show()

        grid.addWidget(browser,0)
        self.setLayout(grid)