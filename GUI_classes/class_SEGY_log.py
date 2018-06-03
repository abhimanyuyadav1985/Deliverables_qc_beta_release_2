from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,decide_and_create_label
from general_functions.SEGY_on_disk_log_parser import extract_from_log
from dug_ops.DUG_ops import return_encoded_log
from configuration.SEGY_header_type_wise import *
from class_pop_up_message_box import pop_up_approval_box
from class_pop_up_text_box import pop_up_text_box_sgyt
from dug_ops.DUG_ops import return_encoded_stripped_sgyt

class SEGY_qc_log(QtGui.QWidget):
    closed = QtCore.pyqtSignal()
    def __init__(self,parent,log_data,title,type):
        super(SEGY_qc_log, self).__init__()
        self.parent = parent

        self.log_path = title
        self.log_data = log_data
        self.type = type

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.setWindowTitle(title)
        self.grid = QtGui.QGridLayout()

        self.text_box = QtGui.QTextEdit()

        self.text_box.setStyleSheet('''
            QTextEdit {
                font: 10pt "Consolas";
            }
        ''')
        self.text_box.setPlainText(log_data)
        self.text_box.setText(log_data)
        self.text_box.setMinimumWidth(500)
        self.grid.addWidget(self.text_box,0,0)
        self.extractor_disp = SEGY_qc_log_extractor(self)
        self.extractor_disp.setFixedWidth(500)
        self.grid.addWidget(self.extractor_disp,0,1)
        self.setLayout(self.grid)


class SEGY_qc_log_extractor(QtGui.QWidget):

    def __init__(self,parent):# type will decide which headers are relevant to be extracted
        super (SEGY_qc_log_extractor,self).__init__()
        self.parent = parent

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.log_path = self.parent.log_path
        self.log_data = self.parent.log_data
        self.type = self.parent.type

        self.grid = QtGui.QGridLayout()

        self.grid.addWidget(create_central_labels(str('Automatic header extraction: ' + type_name_dict[self.type])), 0, 0, 1,3)  # label from type name dict

        self.scroll_area = QtGui.QScrollArea()
        self.grid.addWidget(self.scroll_area,1,0,25,3)

        self.widget = SEGY_header_extraction(self)
        self.scroll_area.setWidget(self.widget)


        pb_ok = QtGui.QPushButton('Save automatic')
        pb_ok.clicked.connect(self.widget.save_auto)
        self.grid.addWidget(pb_ok,26,0,1,1)

        # pb_manual = QtGui.QPushButton('Save Manual')
        # pb_manual.clicked.connect(self.widget.save_manual)
        # self.grid.addWidget(pb_manual,26,2,1,1,)

        self.setLayout(self.grid)


class SEGY_header_extraction(QtGui.QWidget):
    def __init__(self,parent):
        super(SEGY_header_extraction,self).__init__()

        self.parent = parent
        self.log_data = self.parent.log_data
        self.type = self.parent.type
        self.log_path = self.parent.log_path

        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj

        self.grid = QtGui.QGridLayout()

        self.add_general_labels_and_widgets()

        self.def_dict = type_dict[self.type]
        self.extracted_headers_dict = extract_from_log(self.log_data,self.type)

        self.add_type_specific_gui_obj()

        self.check_sgyt_used_aganist_exported_and_add_gui()

        self.setLayout(self.grid)


    def add_general_labels_and_widgets(self):
        #SEGY file_name
        self.grid.addWidget(create_central_labels('SEGY file name'), 0, 0)
        self.segy_name = QtGui.QLabel()
        self.grid.addWidget(self.segy_name, 0, 1)
        # Add general information labels like SGYT name
        self.grid.addWidget(create_central_labels('SGYT name'),1,0)
        self.sgyt_name = QtGui.QLabel()
        self.grid.addWidget(self.sgyt_name,1,1)
        # Number of traces in SEGY file
        self.grid.addWidget(create_central_labels('# Traces'),2,0)
        self.no_traces = QtGui.QLabel()
        self.grid.addWidget(self.no_traces,2,1)
        # File size
        self.grid.addWidget(create_central_labels('File size in Mib'), 3, 0)
        self.file_size = QtGui.QLabel()
        self.grid.addWidget(self.file_size, 3, 1)
        # Mismatch flag
        self.grid.addWidget(create_central_labels('SGYT match flag'),4,0)


    def add_type_specific_gui_obj(self):
        label_list = self.def_dict['ordered_key_list']
        #Now resolve stat values for varous labels
        label_position_dict = self.def_dict['label_start_dict']
        for i in range(0,len(label_list)):
            self.grid.addWidget(create_central_labels(label_list[i]),label_position_dict[label_list[i]],0,1,2)
        # Now add label_list_wise_object
        self.line_edit_dict = {}
        for i in range(0,len(label_list)):
            key = label_list[i]
            row_no = label_position_dict[key]
            dict_to_use = self.def_dict[key]
            for a_key in dict_to_use.keys():
                offset = dict_to_use[a_key][1]
                self.grid.addWidget(create_central_labels(a_key),row_no+offset,0)
                self.line_edit_dict[dict_to_use[a_key][0]] = QtGui.QLabel()
                self.grid.addWidget(self.line_edit_dict[dict_to_use[a_key][0]], row_no + offset, 1)
                #This part only adds the text for binary and trace headers
                if dict_to_use[a_key][0] in self.extracted_headers_dict.keys():
                    self.line_edit_dict[dict_to_use[a_key][0]].setText(str(self.extracted_headers_dict[dict_to_use[a_key][0]]))


    def check_sgyt_used_aganist_exported_and_add_gui(self):
        db_obj = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_qc_log_path == self.log_path).first()
        #--------------------------------------------------------------------------------------------
        exported_sgyt_path = db_obj.sgyt_unix_path
        user_sgyt_path = db_obj.sgyt_user_path

        if return_encoded_stripped_sgyt(self.DUG_connection_obj,exported_sgyt_path) == return_encoded_stripped_sgyt(self.DUG_connection_obj,user_sgyt_path):
            sgyt_verification = True
        else:
            sgyt_verification = False
        # Now populate segy file path
        self.segy_name.setText(db_obj.segy_on_disk_file_path)
        # Now add mismatch flag
        self.sgyt_mismatch_flag = decide_and_create_label(sgyt_verification)
        self.grid.addWidget(self.sgyt_mismatch_flag, 4, 1)
        #Now add trace count
        self.no_traces.setText(str(self.extracted_headers_dict['trace_count']))
        self.file_size.setText(str(self.extracted_headers_dict['file_size']))
        #Now add ebcdic_related_headers if sgyt_verification is True
        #creeate EBCDIC key list
        ebcdic_sgyt_mapper_dict = {}
        dict_ebcdic = self.def_dict['ebcdic']
        for key in dict_ebcdic.keys():
            key_to_use = dict_ebcdic[key][0]
            data_to_use = dict_ebcdic[key][2][0]
            ebcdic_sgyt_mapper_dict.update({key_to_use:data_to_use})
        if sgyt_verification:
            self.sgyt_name.setText(db_obj.sgyt_unix_path)
            db_obj_dict = db_obj.__dict__
            # print db_obj_dict
            # print self.line_edit_dict.keys()
            for key in db_obj_dict.keys():
                if key in ebcdic_sgyt_mapper_dict.keys():
                    self.line_edit_dict[key].setText(str(db_obj_dict[ebcdic_sgyt_mapper_dict[key]]))
        else:
            self.diff_file_name = str('sgyt_diff_') + self.segy_name.text()
            cmd = 'diff ' + exported_sgyt_path + " " + user_sgyt_path
            stdin, stdout, stderr =  self.DUG_connection_obj.ws_client.exec_command(cmd)
            self.pop_up_diff = pop_up_text_box_sgyt(stdout.readlines(),'SGT difference')
            self.pop_up_diff.show()
            self.sgyt_name.setText(db_obj.sgyt_unix_path)
            db_obj_dict = db_obj.__dict__
            # print db_obj_dict
            # print self.line_edit_dict.keys()
            for key in db_obj_dict.keys():
                if key in ebcdic_sgyt_mapper_dict.keys():
                    self.line_edit_dict[key].setText(str(db_obj_dict[ebcdic_sgyt_mapper_dict[key]]))

        self.db_obj_update = db_obj
        self.db_obj_dict  = db_obj_dict
        self.ebcdic_sgyt_mapper_dict = ebcdic_sgyt_mapper_dict
        self.sgyt_match_flag = sgyt_verification

    def save_auto(self):
        # This step should save the db_entries from automatically extracted values
        #1 from extracted headers
        print "Now automatically updating these values to the database.."
        for a_key in self.extracted_headers_dict.keys():
            print a_key + " : " + str(self.extracted_headers_dict[a_key])
        for key, value in self.extracted_headers_dict.iteritems():
            setattr(self.db_obj_update, key, value)
        #2 sgyt to EBCDIC
        #1st create the dic to use to update
        ebcdic_update_dict_to_use = {}
        for key in self.ebcdic_sgyt_mapper_dict.keys():
            ebcdic_update_dict_to_use.update({key: self.db_obj_dict[self.ebcdic_sgyt_mapper_dict[key]]})
        self.ebcdic_update_dict = ebcdic_update_dict_to_use
        #Now update ebcdic related values from the dict
        for a_key in ebcdic_update_dict_to_use.keys():
            print a_key + " : " + str(ebcdic_update_dict_to_use[a_key])
        for key, value in ebcdic_update_dict_to_use.iteritems():
            setattr(self.db_obj_update, key, value)
        #Now create the flags dict
        self.create_flags_dict()
        #Now update using the flags dict
        for key in self.flag_dict.keys():
            print key + " : " + str(self.flag_dict[key])
        for key, value in self.flag_dict.iteritems():
            setattr(self.db_obj_update, key, value)
        #set manual overridde flag to False
        self.db_obj_update.header_manual_override = False
        self.db_obj_update.header_extraction_flag = True
        self.db_connection_obj.sess.commit()


    def create_flags_dict(self):
        self.flag_dict = {}
        function_translator_dict = {
            'sgyt_imp_exp_match_flag': 'self.sgyt_imp_exp_flag()',
            'trc_coordinate_zero_flag' : 'self.trc_coordinate_zero_flag()',
            'trc_type_flag' : 'self.trc_type_flag()',
            'wb_zero_flag' : 'self.wb_zero_flag()',
            'ffid_match_flag' : 'self.ffid_match_flag()',
            'sp_match_flag' : 'self.sp_match_flag()',
            'il_match_flag' : 'self.il_match_flag()',
            'xl_match_flag' : 'self.xl_match_flag()'
        }
        for a_flag in self.def_dict['flag_list']:
            flag_function = function_translator_dict[a_flag]
            eval(flag_function)

    def sgyt_imp_exp_flag(self):
        self.flag_dict.update({'sgyt_imp_exp_match_flag': self.sgyt_match_flag})

    def trc_coordinate_zero_flag(self):
        coordinates_list = self.def_dict['coordinate_flag_list']
        coordinate_flag = True
        for a_header in coordinates_list:
            if int(self.extracted_headers_dict[a_header]) == 0:
                coordinate_flag = False

        self.flag_dict.update({'trc_coordinate_zero_flag': coordinate_flag })

    def trc_type_flag(self):
        if int(self.extracted_headers_dict['trc_min_trc_flag']) == int(self.extracted_headers_dict['trc_max_trc_flag']):
            self.flag_dict.update({'trc_type_flag': False})
        else:
            self.flag_dict.update({'trc_type_flag': True})

    def wb_zero_flag(self):
        if int(self.extracted_headers_dict['trc_min_wb']) == 0:
            self.flag_dict.update({'wb_zero_flag' : False})
        else:
            self.flag_dict.update({'wb_zero_flag': True})

    def ffid_match_flag(self):
        self.flag_dict.update({'ffid_match_flag': False})
        if int(self.ebcdic_update_dict['ebcdic_min_ffid']) == int(self.extracted_headers_dict['trc_min_ffid']):
            if int(self.ebcdic_update_dict['ebcdic_max_ffid']) == int(self.extracted_headers_dict['trc_max_ffid']):
                self.flag_dict.update({'ffid_match_flag': True})

    def sp_match_flag(self):
        self.flag_dict.update({'sp_match_flag':False})
        ebcdic_sp_list = [int(self.ebcdic_update_dict['ebcdic_fgsp']),int(self.ebcdic_update_dict['ebcdic_lgsp'])]
        trc_sp_list = [int(self.extracted_headers_dict['trc_min_sp']),int(self.extracted_headers_dict['trc_max_sp'])]
        if min(ebcdic_sp_list) == min(trc_sp_list):
            if max(ebcdic_sp_list) == max(trc_sp_list):
                self.flag_dict.update({'sp_match_flag': True})

    def il_match_flag(self):
        self.flag_dict.update({'il_match_flag':False})
        if int(self.ebcdic_update_dict['ebcdic_min_il']) == int(self.extracted_headers_dict['trc_min_il']):
            if int(self.ebcdic_update_dict['ebcdic_max_il']) == int(self.extracted_headers_dict['trc_max_il']):
                self.flag_dict.update({'il_match_flag': True})

    def xl_match_flag(self):
        self.flag_dict.update({'xl_match_flag': False})
        if int(self.ebcdic_update_dict['ebcdic_min_xl']) == int(self.extracted_headers_dict['trc_min_xl']):
            if int(self.ebcdic_update_dict['ebcdic_max_xl']) == int(self.extracted_headers_dict['trc_max_xl']):
                self.flag_dict.update({'xl_match_flag': True})

class approve_form_SEGY_on_disk_qc(QtGui.QWidget):
    def __init__(self,parent,type):
        super(approve_form_SEGY_on_disk_qc,self).__init__()
        self.parent = parent
        db_obj_dict = self.parent.db_obj_update.__dict__

        self.def_dict = type_dict[type]

        self.grid = QtGui.QGridLayout()
        #Add label
        label_text = str('Approval form : ' + type_name_dict[type])
        self.grid.addWidget(create_central_labels(label_text),0,0,1,2)
        flag_list_to_use = self.def_dict['flag_list']

        for i in range(0,len(flag_list_to_use)):
            self.grid.addWidget(create_central_labels(flag_name_dict[flag_list_to_use[i]]),i+1,0)
            self.grid.addWidget(decide_and_create_label(db_obj_dict[flag_list_to_use[i]]),i+1,1)
        message = 'Approve or reject: ' + db_obj_dict['segy_on_disk_file_path']

        self.approve_box = pop_up_approval_box(message = message)
        self.approve_box.closed.connect(self.parent.approve_qc_log)

        self.grid.addWidget(self.approve_box,len(flag_list_to_use)+2,0,1,2)

        self.setLayout(self.grid)











