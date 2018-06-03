import sys
from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,create_center_blank
from general_functions.general_functions import get_item_through_dialogue


class pop_up_check_combo_box_media_association(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent,title,combo_list,(a,b),(c,d)):
        super(pop_up_check_combo_box_media_association, self).__init__()

        self.deliverable = c
        self.set_no = d
        self.shipment_no = a
        self.box_no = b
        self.media_list = combo_list

        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.setWindowTitle(title)

        self.widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()

        self.media_dict = {}

        i = 0

        for media in combo_list:
            key = str(media.media_label + " : " + media.reel_no)
            btn = QtGui.QCheckBox(str(media.media_label + " : " + media.reel_no))
            btn.setObjectName(str(media.media_label + " : " + media.reel_no))
            if media.shipment_no == a and media.box_no == b:
                btn.setChecked(True)
                data = True
            else:
                btn.setChecked(False)
                data = False
            self.media_dict.update({key: data})
            btn.stateChanged.connect(self.btnstate)

            grid.addWidget(btn, i, 0)

            i = i+1


        pb_ok = QtGui.QPushButton("OK")
        pb_ok.clicked.connect(self.ok_return)



        self.setMinimumWidth(300)
        self.widget.setLayout(grid)
        scroll = QtGui.QScrollArea()
        scroll.setWidget(self.widget)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(600)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(create_central_labels(a), 0)
        layout.addWidget(create_central_labels(str("Box no : " + str(d))), 1)
        layout.addWidget(create_central_labels(str(c.id) + "_" + c.name), 2)
        layout.addWidget(create_central_labels(str("Set no: " + str(d))), 3)
        layout.addWidget(create_center_blank(" Available Media list (Media Label : Reel_no) "), 4)
        layout.addWidget(scroll,5)
        layout.addWidget(pb_ok,6)

        self.show()

    def btnstate(self):
        sender =  self.sender()
        name = str(sender.objectName())
        if self.media_dict[name] == True:
            self.media_dict[name] = False
        else:
            self.media_dict[name] = True


    def ok_return(self):
        # print "Now printing the state......."
        # for key in self.media_dict.keys():
        #     print key, str(self.media_dict[key])

        # now check and add the tapes to the database
        for media in self.media_list:
            if self.media_dict[str(media.media_label + " : " + media.reel_no)] == True:
                # check if this entry already exists in db
                    if media.shipment_no is None:
                        print "Now creating association for deliverable: " + self.deliverable.name + " set no: " + str(self.set_no) + " media : " + media.media_label
                        self.create_new_association(media.t_id)
                    else:
                        print "This media already belongs to a deliverable, press y to set the last one to bad and the current one to good"
                        status = get_item_through_dialogue(self,"This media already belongs to a deliverable, press y to set the last one to bad and the current one to good press y to continue")
                        if status == 'y':
                            self.change_and_create_association(media.t_id,media.media_label)
                        else:
                            pass

        self.close()



    def create_new_association(self,id):
        media_list_dao = self.db_connection_obj.sess.query(self.db_connection_obj.Media_list).filter(self.db_connection_obj.Media_list.t_id == id).first()
        media_list_dao.shipment_no = self.shipment_no
        media_list_dao.box_no = self.box_no
        media_list_dao.use_tag = True
        self.db_connection_obj.sess.commit()



    def change_and_create_association(self,id,media_label):
        print "Now Nullifying the old assocation for deliverable: " + self.deliverable.name + " set no: " + str(self.set_no) + " media : " + media_label
        media_list_dao = self.db_connection_obj.sess.query(self.db_connection_obj.Media_list).filter(self.db_connection_obj.Media_list.t_id == id).first()
        media_list_dao.shipment_no = self.shipment_no
        media_list_dao.box_no = self.box_no
        media_list_dao.use_tag = False
        self.db_connection_obj.sess.commit()
        print "Now creating association for deliverable: " + self.deliverable.name + " set no: " + str(self.set_no) + " media : " + media_label
        new_obj = self.db_connection_obj.Media_list()
        new_obj.deliverable_id = self.deliverable_id
        new_obj.set_no = self.set_no
        new_obj.shipment_no = self.shipment_no
        new_obj.box_no = self.box_no
        new_obj.media_label = media_label
        new_obj.use_tag = True
        self.db_connection_obj.sess.add(new_obj)
        self.db_connection_obj.sess.commit()




