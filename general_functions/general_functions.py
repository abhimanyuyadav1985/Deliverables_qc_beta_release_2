from PyQt4 import QtGui, QtCore
import datetime

####################################################################################################################################
###Global Misc functions
####################################################################################################################################

def create_central_labels(label_text):
    labels_widget = QtGui.QLabel(label_text)
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
    labels_widget.setStyleSheet('background-color: rgb(65,65,65);color: white')
    return labels_widget

def create_true_label():
    labels_widget = QtGui.QLabel("True")
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
    labels_widget.setStyleSheet('background-color: green;color: white')
    return labels_widget

def create_false_label():
    labels_widget = QtGui.QLabel("False")
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
    labels_widget.setStyleSheet('background-color: red;color: white')
    return labels_widget

def create_yellow_label():
    labels_widget = QtGui.QLabel("Ready")
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
    labels_widget.setStyleSheet('background-color: yellow ;color: red')
    return labels_widget

def create_blue_label():
    labels_widget = QtGui.QLabel("Running")
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
    labels_widget.setStyleSheet('background-color: blue ;color: white')
    return labels_widget

def create_center_data(data_text):
    labels_widget = QtGui.QLabel(data_text)
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    labels_widget.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
    return labels_widget

def create_center_blank(data_text):
    labels_widget = QtGui.QLabel(data_text)
    labels_widget.setAlignment(QtCore.Qt.AlignCenter)
    return labels_widget

def create_left_blank(data_text,color_text):
    labels_widget = QtGui.QLabel(data_text)
    labels_widget.setAlignment(QtCore.Qt.AlignLeft)
    color_cmd = 'Color :'+ color_text
    labels_widget.setStyleSheet(color_cmd)
    return labels_widget

def decide_and_create_label(data_text):
    if str(data_text) == 'True':
        label_widget = create_true_label()
    elif str(data_text) == 'False':
        label_widget = create_false_label()
    elif str(data_text) == 'Running':
        label_widget = create_blue_label()
    else:
        label_widget = create_yellow_label()
    return label_widget


def get_item_through_dialogue(obj,top_message):
    text, ok = QtGui.QInputDialog.getText(obj,top_message,top_message)
    if ok:
        return str(text)

def change_log_creation(gui,conn_obj, message,type_entry,location):
    text, ok = QtGui.QInputDialog.getText(gui, message, message)
    if ok:
        user_name, ok_u = QtGui.QInputDialog.getText(gui, "Enter name for the change log", "Enter name for the change log")
        if ok_u:
            choice, ok1 = QtGui.QInputDialog.getText(gui, "Type y to confirm", "Type y to confirm")
            if ok1:
                if choice == "y":
                    new_change_log = conn_obj.change_log()
                    new_change_log.type_entry = type_entry
                    new_change_log.location = location
                    new_change_log.details = str(message + " reason : " + text)
                    new_change_log.date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
                    new_change_log.user_name = str(user_name)
                    conn_obj.sess.add(new_change_log)
                    conn_obj.sess.commit()
                    return True
                else:
                    return False
        else:
            return False
    else:
        return False

if __name__ == '__main__':
    pass