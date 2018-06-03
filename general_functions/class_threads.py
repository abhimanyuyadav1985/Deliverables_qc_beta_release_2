from PyQt4 import QtCore
from GUI_classes.class_pop_up_message_box import pop_up_message_box

class Worker(QtCore.QThread):

    def __init__(self,type):
        super(Worker,self).__init__()
        self.type = type

    def start_work(self,gui):
        if self.type == "excel":
            message_print = "A win32 mode excel application will start working in invisible mode now, please save all your excel work and close any open excel workbooks, press ok to start !!!"
            gui.pop_up_message_box = pop_up_message_box(message=message_print,type='Warning')
            gui.pop_up_message_box.show()
            gui.pop_up_message_box.closed.connect(self.start_now)
        else:
            self.start_now()

    def start_now(self):
        self.start()

