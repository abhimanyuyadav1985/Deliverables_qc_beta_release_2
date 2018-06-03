from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels, create_center_data, create_left_blank,create_true_label,create_false_label
from dug_ops.segy_templ import encode_file,decode_string,return_ebcdic_from_sgyt
from database_engine.DB_ops import add_deliverable, fetch_single_deliverable
from configuration import *
from general_functions.class_deliverables_dir_service import deliverable_dir_service
from class_pop_up_combo_box import pop_up_combo_box
from general_functions.general_functions import get_item_through_dialogue
from database_engine.DB_ops import fetch_deliverable_objects_list
from general_functions.class_change_paths_for_usb_service import change_usb_deliverable_paths
from general_functions.general_functions import change_log_creation
from configuration import deliverable_type_list
from configuration.Tool_tips import tool_tips_mapper_dict


class add_new_deliverable(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent):
        # define the top window

        super(add_new_deliverable, self).__init__(parent=parent)
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj# use this line to pass the connection object between the parent and the child
        self.tool_tip_dict = tool_tips_mapper_dict['single_deliverable']
        self.setToolTip(self.tool_tip_dict['general'])

        self.dir_service = deliverable_dir_service(self)

        grid = QtGui.QGridLayout()
        #-------------------------------------------
        #add title
        #-------------------------------------------
        grid.addWidget(create_central_labels('New deliverable description'),0,0,1,2)
        #--------------------------------------------
        # deliverable attributes
        #--------------------------------------------
        keys_list = ['id','name','class_d','type','media','copies','prod_version','reel_prefix','sgyt','bin_def','trc_def',]
        keys_dict = {}
        keys_dict['id'] = create_center_data('Automatic')
        keys_dict['name'] = QtGui.QLineEdit()
        class_choice =  QtGui.QComboBox()
        class_choice.addItems(deliverable_classes)
        keys_dict['class_d'] = class_choice
        type_choice = QtGui.QComboBox()
        type_choice.addItems(deliverable_type_list)
        keys_dict['type'] = type_choice
        media_choice = QtGui.QComboBox()
        media_choice.addItems(valid_media_list)
        keys_dict['media'] = media_choice
        keys_dict['copies'] = QtGui.QLineEdit()
        keys_dict['prod_version'] = QtGui.QLineEdit()
        keys_dict['sgyt'] = QtGui.QLineEdit()
        keys_dict['bin_def'] = QtGui.QLineEdit()
        keys_dict['trc_def'] = QtGui.QLineEdit()
        keys_dict['reel_prefix'] = QtGui.QLineEdit()

        for a_key in keys_list:
            keys_dict[a_key].setToolTip(self.tool_tip_dict[a_key])


        self.deliverable_def = keys_dict

        pb_sgyt = QtGui.QPushButton()
        pb_sgyt.setText('Select SGYT file')
        pb_sgyt.clicked.connect(self.browse_sgyt)


        pb_bin_def = QtGui.QPushButton()
        pb_bin_def.setText('Select bin.def file')
        pb_bin_def.clicked.connect(self.browse_bin_def)

        pb_trc_def = QtGui.QPushButton()
        pb_trc_def.setText('Select trc.def file')
        pb_trc_def.clicked.connect(self.browse_trc_def)

        for i in range(0,len(keys_list)):
            grid.addWidget(create_central_labels(str(keys_list[i])),i+1,0)
            grid.addWidget(keys_dict[keys_list[i]],i+1,1)

        grid.addWidget(pb_sgyt,9,2)
        grid.addWidget(pb_bin_def,10,2)
        grid.addWidget(pb_trc_def,11,2)


        j = len(keys_list)

        self.pb_save = QtGui.QPushButton()
        self.pb_save.setText('Save')
        self.pb_save.setStatusTip('Save deliverable to the database')
        self.pb_save.clicked.connect(self.save_deliverable)

        grid.addWidget(self.pb_save,j+1,0)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Back')
        self.pb_exit.setStatusTip('Back to main deliverables Menu')
        self.pb_exit.clicked.connect(self.parent.set_deliverables_window)

        grid.addWidget(self.pb_exit, j + 2, 0)

        self.setLayout(grid)


    def browse_sgyt(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
        self.deliverable_def['sgyt'].setText(fname)
        self.show()

    def browse_bin_def(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
        self.deliverable_def['bin_def'].setText(fname)
        self.show()

    def browse_trc_def(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
        self.deliverable_def['trc_def'].setText(fname)
        self.show()

    def save_deliverable(self):
        print "Now converting the GUI object to DAO....",
        new_deliverable = self.adaptar_gui_to_object()

        print "Done .....now saving it........"
        #---------------------------------------------------------------
        #------------use of DIR service
        #---------------------------------------------------------------
        name = new_deliverable.name
        add_deliverable(self.db_connection_obj, new_deliverable)
        print "done .... "
        self.dir_service.set_deliverable(new_deliverable)
        self.dir_service.create_all_paths()
        self.dir_service.add_all_paths_to_db()
        if new_deliverable.media == 'USB':
            status = get_item_through_dialogue(self,"The media is USB, do you want to associate the deliverable directories with another deliverable, press y to continue")
            if status == 'y':
                self.usb_deliverable = new_deliverable
                self.choose_deliverable("change_deliverable_dir")
        #---------------------------------------------------------------
        self.parent.set_deliverables_window()

    def choose_deliverable(self, ops):
        deliverables_list = fetch_deliverable_objects_list(self.db_connection_obj)
        disp_name_dict = {}
        combo_item_list = []
        for deliverable in deliverables_list:
            key = str(deliverable.id) + "_" + deliverable.name
            data = deliverable
            disp_name_dict.update({key: data})
            combo_item_list.append(key)
        self.disp_name_dict = disp_name_dict
        self.pop_up_combo_box = pop_up_combo_box(self, "Select deliverable", combo_item_list, 'deliverable', ops)
        self.pop_up_combo_box.show()

    def set_attribute(self, attribute, caller, ops):
        if ops == 'change_deliverable_dir':
            if caller == 'deliverable':
                self.ref_deliverable = self.disp_name_dict[attribute]
                change_usb_deliverable_paths(self,self.usb_deliverable,self.ref_deliverable)


    def adaptar_gui_to_object(self):
        new_deliverable = self.db_connection_obj.Deliverables()
        new_deliverable.name = str(self.deliverable_def['name'].text())
        new_deliverable.class_d = str(self.deliverable_def['class_d'].currentText())
        new_deliverable.type = str(self.deliverable_def['type'].currentText())
        new_deliverable.media = str(self.deliverable_def['media'].currentText())
        new_deliverable.copies = str(self.deliverable_def['copies'].text())
        new_deliverable.prod_version = str(self.deliverable_def['prod_version'].text())
        new_deliverable.reel_prefix = str(self.deliverable_def['reel_prefix'].text())
        if os.path.exists(self.deliverable_def['sgyt'].text()):
            new_deliverable.path_sgyt = str(self.deliverable_def['sgyt'].text())
            new_deliverable.sgyt = encode_file(self.deliverable_def['sgyt'].text())
            new_deliverable.sgyt_master_status = True
        if os.path.exists(self.deliverable_def['bin_def'].text()):
            new_deliverable.path_bin_def = str(self.deliverable_def['bin_def'].text())
            new_deliverable.bin_def = encode_file(self.deliverable_def['bin_def'].text())
            new_deliverable.bin_def_status = True
        if os.path.exists(self.deliverable_def['trc_def'].text()):
            new_deliverable.path_trc_def = str(self.deliverable_def['trc_def'].text())
            new_deliverable.trc_def = encode_file(self.deliverable_def['trc_def'].text())
            new_deliverable.trc_def_status = True
        new_deliverable.active_status = True
        return new_deliverable


class view_single_deliverable_detail(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent,id):
        # define the top window

        super(view_single_deliverable_detail, self).__init__(parent=parent)
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj  # use this line to pass the connection object between the parent and the child
        grid = QtGui.QGridLayout()
        # -------------------------------------------
        # add title
        # -------------------------------------------
        grid.addWidget(create_central_labels('Details for the deliverable'), 0, 0, 1, 2)
        keys_list = ['id', 'name', 'class_d', 'type', 'media', 'copies', 'prod_version','reel_prefix','sgyt_master_status','bin_def_status','trc_def_status','active_status','sgyt','bin_def','trc_def', ]
        result = fetch_single_deliverable(self.db_connection_obj,id)
        grid.addWidget(create_central_labels('Existing deliverable details'), 0, 0, 1, 2)

        self.id = id
        self.result = result

        for j in range(0,len(keys_list)):
            grid.addWidget(create_center_data(str(keys_list[j])),j+1,0)

        for j in range(0,8):
            grid.addWidget(create_left_blank(str(result[keys_list[j]]),"blue"),j+1,1)

        for j in range(9,12):
            if result[str(keys_list[j])] is True:
                grid.addWidget(create_true_label(),j+1,1)
            else:
                grid.addWidget(create_false_label(), j + 1, 1)
                if j !=10:
                    grid.addWidget(create_left_blank('No data to show','red'),j+5,1)


        path_keys = ['path_sgyt','path_bin_def','path_trc_def']

        for i in range(0,len(path_keys)):
            grid.addWidget(create_center_data(str(path_keys[i])),i+16,0)
            if result[path_keys[i]] is not None:
                grid.addWidget(create_left_blank(str(result[path_keys[i]]),'blue'), i + 16, 1)
            else:
                grid.addWidget(create_left_blank('No file selected so far','red'), i + 16, 1)

        if result['sgyt_master_status'] is True:
            self.pb_show_sgyt = QtGui.QPushButton()
            self.pb_show_sgyt.setText('Show EBCDIC only')
            self.pb_show_sgyt.setStatusTip('Show the DUG segyt file associated with the deliverable')
            self.pb_show_sgyt.clicked.connect(self.show_ebcdic)
            grid.addWidget(self.pb_show_sgyt,13,1)

        if result['bin_def_status'] is True:
            self.pb_show_bin = QtGui.QPushButton()
            self.pb_show_bin.setText('Show Bin.def')
            self.pb_show_bin.setStatusTip('Show the DUG segyt file associated with the deliverable')
            self.pb_show_bin.clicked.connect(self.show_bin_def)
            grid.addWidget(self.pb_show_bin, 14, 1)

        if result['trc_def_status'] is True:
            self.pb_show_trc = QtGui.QPushButton()
            self.pb_show_trc.setText('Show Trc.def')
            self.pb_show_trc.setStatusTip('Show the DUG segyt file associated with the deliverable')
            self.pb_show_trc.clicked.connect(self.show_trc_def)
            grid.addWidget(self.pb_show_trc, 15, 1)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Exit')
        self.pb_exit.clicked.connect(self.parent.set_deliverables_window)
        grid.addWidget(self.pb_exit,19,0)
        self.setLayout(grid)

    def show_ebcdic(self):
        sgyt_string = decode_string(str(self.result['sgyt']))
        ebcdic = return_ebcdic_from_sgyt(sgyt_string)
        title = str(self.result['id']) + " " + str(self.result['name']) + ' EBCDIC'
        self.ebcdic_text_box = pop_up_text_box_view_only("", title)
        for i in range(0, 3201, 80):
            self.ebcdic_text_box.text_edit.append(ebcdic[i:i + 80])
        self.ebcdic_text_box.closed.connect(self.show)
        self.ebcdic_text_box.resize(600,700)
        self.ebcdic_text_box.show()

    def show_bin_def(self):
        bin_def = decode_string(str(self.result['bin_def']))
        title = str(self.result['id'])+ " " + str(self.result['name']) + ' Bin.def'
        self.bin_def_text_box = pop_up_text_box_view_only(bin_def,title)
        self.bin_def_text_box.closed.connect(self.show)
        self.bin_def_text_box.resize(700,600)
        self.bin_def_text_box.show()

    def show_trc_def(self):
        trc_def = decode_string(str(self.result['trc_def']))
        title = str(self.result['id']) + " " + str(self.result['name']) + ' Trc.def'
        self.trc_def_text_box = pop_up_text_box_view_only(trc_def, title)
        self.trc_def_text_box.closed.connect(self.show)
        self.trc_def_text_box.resize(700, 1000)
        self.trc_def_text_box.show()

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

class edit_single_deliverable(QtGui.QWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, parent, id):
        # define the top window

        super(edit_single_deliverable, self).__init__(parent=parent)
        self.parent = parent
        self.id = id
        self.db_connection_obj = self.parent.db_connection_obj  # use this line to pass the connection object between the parent and the child
        grid = QtGui.QGridLayout()
        # -------------------------------------------
        # add title
        # -------------------------------------------
        grid.addWidget(create_central_labels('Edit single Deliverable'), 0, 0, 1, 2)

        self.db_connection_obj.sess = self.db_connection_obj.Session()
        self.new_deliverable = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables).filter(self.db_connection_obj.Deliverables.id == id).first()

        self.result = self.new_deliverable.__dict__


        keys_list = ['id', 'name', 'class_d', 'type', 'media', 'copies', 'prod_version', 'reel_prefix','sgyt', 'bin_def', 'trc_def']
        keys_dict = {}
        keys_dict['id'] = create_center_data(str(self.result['id']))
        keys_dict['name'] = QtGui.QLineEdit()
        class_choice = QtGui.QComboBox()
        class_choice.addItems(deliverable_classes)
        keys_dict['class_d'] = class_choice
        type_choice = QtGui.QComboBox()
        type_choice.addItems(deliverable_type_list)
        keys_dict['type'] = type_choice
        media_choice = QtGui.QComboBox()
        media_choice.addItems(valid_media_list)
        keys_dict['media'] = media_choice
        keys_dict['copies'] = QtGui.QLineEdit()
        keys_dict['prod_version'] = QtGui.QLineEdit()
        keys_dict['reel_prefix'] = QtGui.QLineEdit()
        keys_dict['sgyt'] = QtGui.QLineEdit()
        keys_dict['bin_def'] = QtGui.QLineEdit()
        keys_dict['trc_def'] = QtGui.QLineEdit()

        self.deliverable_def = keys_dict

        pb_sgyt = QtGui.QPushButton()
        pb_sgyt.setText('Select SGYT file')
        pb_sgyt.clicked.connect(self.browse_sgyt)

        pb_bin_def = QtGui.QPushButton()
        pb_bin_def.setText('Select bin.def file')
        pb_bin_def.clicked.connect(self.browse_bin_def)

        pb_trc_def = QtGui.QPushButton()
        pb_trc_def.setText('Select trc.def file')
        pb_trc_def.clicked.connect(self.browse_trc_def)

        for i in range(0, len(keys_list)):
            grid.addWidget(create_central_labels(str(keys_list[i])), i + 1, 0)
            grid.addWidget(keys_dict[keys_list[i]], i + 1, 1)

        grid.addWidget(pb_sgyt, 9, 2)
        grid.addWidget(pb_bin_def, 10, 2)
        grid.addWidget(pb_trc_def, 11, 2)

        j = len(keys_list)

        self.pb_save = QtGui.QPushButton()
        self.pb_save.setText('Update')
        self.pb_save.setStatusTip('Save deliverable to the database')
        self.pb_save.clicked.connect(self.update_deliverable)

        grid.addWidget(self.pb_save, j + 1, 0)

        self.pb_exit = QtGui.QPushButton()
        self.pb_exit.setText('Back')
        self.pb_exit.setStatusTip('Back to main deliverables Menu')
        self.pb_exit.clicked.connect(self.parent.set_deliverables_window)

        grid.addWidget(self.pb_exit, j + 2, 0)

        self.object_to_gui()

        self.setLayout(grid)


    def browse_sgyt(self):
        message = str("Please enter the reason for the change in SGYT file for the deliverable id : " + self.id)
        perform = change_log_creation(gui = self, conn_obj=self.db_connection_obj,message=message,type_entry="change",location="deliverables.sgyt")
        if perform:
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
            self.deliverable_def['sgyt'].setText(fname)
            self.show()

    def browse_bin_def(self):
        message = str("Please enter the reason for the change in Bin.def file for the deliverable id : " + self.id)
        perform = change_log_creation(gui = self, conn_obj=self.db_connection_obj,message=message,type_entry="change",location="deliverables.bin.def")
        if perform:
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
            self.deliverable_def['bin_def'].setText(fname)
            self.show()

    def browse_trc_def(self):
        message = str("Please enter the reason for the change in Trc.def file for the deliverable id : " + self.id)
        perform = change_log_creation(gui = self, conn_obj=self.db_connection_obj,message=message,type_entry="change",location="deliverables.trc.def")
        if perform:
            fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
            self.deliverable_def['trc_def'].setText(fname)
            self.show()

    def update_deliverable(self):
        print "Now converting the GUI object to DAO....",
        new_deliverable = self.adaptar_gui_to_object()
        self.db_connection_obj.sess.commit()
        self.parent.set_deliverables_window()


    def object_to_gui(self):
        self.deliverable_def['name'].setText(str(self.result['name']))
        index = self.deliverable_def['class_d'].findText(str(self.result['class_d']), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.deliverable_def['class_d'].setCurrentIndex(index)
        index = self.deliverable_def['type'].findText(str(self.result['type']), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.deliverable_def['type'].setCurrentIndex(index)
        index = self.deliverable_def['media'].findText(str(self.result['media']), QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.deliverable_def['media'].setCurrentIndex(index)
        self.deliverable_def['copies'].setText(str(self.result['copies']))
        self.deliverable_def['prod_version'].setText(str(self.result['prod_version']))
        self.deliverable_def['reel_prefix'].setText(str(self.result['reel_prefix']))
        if self.result['sgyt_master_status'] is True:
            self.deliverable_def['sgyt'].setText(self.result['path_sgyt'])

        if self.result['bin_def_status'] is True:
            self.deliverable_def['bin_def'].setText(self.result['path_bin_def'])

        if self.result['trc_def_status'] is True:
            self.deliverable_def['trc_def'].setText(self.result['path_trc_def'])


    def adaptar_gui_to_object(self):
        self.new_deliverable.name = str(self.deliverable_def['name'].text())
        self.new_deliverable.class_d = str(self.deliverable_def['class_d'].currentText())
        self.new_deliverable.type = str(self.deliverable_def['type'].currentText())
        self.new_deliverable.media = str(self.deliverable_def['media'].currentText())
        self.new_deliverable.copies = str(self.deliverable_def['copies'].text())
        self.new_deliverable.prod_version = str(self.deliverable_def['prod_version'].text())
        self.new_deliverable.reel_prefix = str(self.deliverable_def['reel_prefix'].text())
        if os.path.exists(self.deliverable_def['sgyt'].text()):
            self.new_deliverable.path_sgyt = str(self.deliverable_def['sgyt'].text())
            self.new_deliverable.sgyt = encode_file(self.deliverable_def['sgyt'].text())
            self.new_deliverable.sgyt_master_status = True
        if os.path.exists(self.deliverable_def['bin_def'].text()):
            self.new_deliverable.path_bin_def = str(self.deliverable_def['bin_def'].text())
            self.new_deliverable.bin_def = encode_file(self.deliverable_def['bin_def'].text())
            self.new_deliverable.bin_def_status = True
        if os.path.exists(self.deliverable_def['trc_def'].text()):
            self.new_deliverable.path_trc_def = str(self.deliverable_def['trc_def'].text())
            self.new_deliverable.trc_def = encode_file(self.deliverable_def['trc_def'].text())
            self.new_deliverable.trc_def_status = True
        self.new_deliverable.active_status = True
