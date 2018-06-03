from  GUI_classes.class_top_window import Top_Window
from  PyQt4 import QtGui
import sys

from app_log import setup_logging

def call_main_window():
    app = QtGui.QApplication(sys.argv)
    setup_logging()
    GUI = Top_Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    call_main_window()