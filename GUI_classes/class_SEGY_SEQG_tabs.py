from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels,create_center_data,decide_and_create_label,change_log_creation
from dug_ops.segy_templ import return_ebcdic_from_sgyt,decode_string
from class_pop_up_message_box import pop_up_message_box,pop_up_approval_box,pop_up_approval_box_segy_write
from dug_ops.DUG_ops import return_encoded_log
from class_pop_up_text_box import pop_up_text_box_view_only
import datetime
from dateutil import parser
from dug_ops.DUG_ops import check_generic_path, get_file_timestamp
import posixpath
from class_SEGY_log import SEGY_qc_log, approve_form_SEGY_on_disk_qc
from configuration import SEGY_write_to_media_table_list
from general_functions.general_functions import get_item_through_dialogue
from configuration.Tool_tips import tool_tips_mapper_dict
from database_engine.DB_ops import get_data_for_SEGY_qc
from dug_ops.DUG_ops import fetch_directory_content_list

import logging, time
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class SEQG_SEGY_status_tabs(QtGui.QTabWidget):
    def __init__(self, parent):
        super(SEQG_SEGY_status_tabs, self).__init__()

        self.parent = parent
        self.overall_sumamry = SEGY_all_summary(self.parent)
        self.sgyt_summary = SEQG_SEGY_SGYT_status(self.parent)
        self.on_disk_summary = SEQG_SEGY_on_disk_QC(self.parent)
        self.write_summary = SEQG_SEGY_write_QC_status(self.parent)

        self.addTab(self.overall_sumamry, 'Summary')
        self.addTab(self.sgyt_summary,'SGYT')
        self.addTab(self.on_disk_summary, 'SEGY on disk')
        self.addTab(self.write_summary,'SEGY write')



class SEGY_all_summary(QtGui.QScrollArea):
    def __init__(self,parent):
        super(SEGY_all_summary, self).__init__()
        self.grid = QtGui.QGridLayout()
        self.title = create_central_labels("SEGY production and QC summary")
        self.title.setFixedHeight(20)
        self.grid.addWidget(self.title,0,0)
        self.setLayout(self.grid)


#----------------------------------------------

class SEQG_SEGY_SGYT_status(QtGui.QScrollArea):

    def __init__(self, parent):
        super(SEQG_SEGY_SGYT_status, self).__init__()
        ts = time.time()
        self.tool_tip_dict = tool_tips_mapper_dict['segy_tabs_2d']
        self.parent = parent
        self.setToolTip(self.tool_tip_dict['sgyt'])
        self.deliverable = self.parent.deliverable

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.deliverable_id = self.parent.deliverable_id
        self.grid = QtGui.QGridLayout()

        # add labels
        self.add_labels()
        self.add_data()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)
        te = time.time()
        time_string = "{:8.5f} sec".format(te - ts)
        logger.info("Finished Creating SEQG SEGY status widget in: " + time_string)
        #self.show()


    def add_labels(self):
        labels_list  = ['Seq_no','Line name','SGYT export','SGYT reel_no','Exported by','Date','QC run status','Approve','Approval status','Approved by','Approval timestamp']
        for i in range(0,len(labels_list)):
            self.grid.addWidget(create_central_labels(labels_list[i]),0,i)

    def add_data(self):
        data = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable.id).order_by(self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc).all()
        #now create a dictinoary for status
        data_dict = {}
        for obj in data:
            key = obj.line_name
            data = obj
            data_dict.update({key:data})
        self.data_dict = data_dict
        #Now search for all available lines that have been shot in orca line
        lines_shot = self.db_connection_obj.sess.query(self.db_connection_obj.Line).order_by(self.db_connection_obj.Line.sequence_number).all()
        line_name_list = []
        for aline in lines_shot:
            if int(aline.sequence_number) < 9000:
                line_name_list.append((aline.sequence_number,aline.real_line_name))
            else:
                pass
        # now add the objects in the line_name_list
        for i in range(1,len(line_name_list)+1):
            self.grid.addWidget(create_center_data(str(line_name_list[i-1][0])),i,0)
            self.grid.addWidget(create_center_data(line_name_list[i - 1][1]), i, 1)
            #now check if some data exists for this in the data_dict
            if line_name_list[i-1][1] in data_dict.keys():
                #if yes
                sgyt_data = data_dict[line_name_list[i-1][1]]
                self.grid.addWidget(decide_and_create_label(str(sgyt_data.sgyt_status)),i,2)
                self.grid.addWidget(create_center_data(sgyt_data.sgyt_reel_no),i,3)
                self.grid.addWidget(create_center_data(sgyt_data.sgyt_exp_uname),i,4)
                self.grid.addWidget(create_center_data(sgyt_data.sgyt_time_stamp),i,5)
                # now add push button to view log
                pb = QtGui.QPushButton("view SGYT")
                pb.setObjectName(line_name_list[i-1][1])
                pb.setToolTip(self.data_dict[line_name_list[i-1][1]].sgyt_unix_path)
                pb.clicked.connect(self.connect_to_log)
                self.grid.addWidget(pb,i,6)
                self.grid.addWidget(decide_and_create_label(str(sgyt_data.sgyt_approval_status)),i,8) # this will automatically decide and create the necessary label True false or blank
                # pb to approve the log
                pb_approval = QtGui.QPushButton("Approve")
                pb_approval.setObjectName(line_name_list[i - 1][1])
                pb_approval.clicked.connect(self.show_approval_popup)
                self.grid.addWidget(pb_approval,i,7)
                #now check and add aprrover name it the approval status is not blank
                if sgyt_data.sgyt_approval_status is not None:
                    self.grid.addWidget(create_center_data(sgyt_data.sgyt_approver_name), i, 9)
                    self.grid.addWidget(create_center_data(sgyt_data.sgyt_approval_time), i, 10)
            else:
                self.grid.addWidget(decide_and_create_label(""), i, 2)

    def show_approval_popup(self):
        sender = self.sender()
        self.obj_name = str(sender.objectName())
        message = str("Approve or Reject the SGYT file for line: " + self.obj_name)
        self.approval_pop_up = pop_up_approval_box(message)
        self.approval_pop_up.closed.connect(self.approve_log)
        self.approval_pop_up.setMinimumWidth(300)
        self.approval_pop_up.show()

    def approve_log(self,user_name,status):
        obj = self.data_dict[self.obj_name]
        if status:
            obj.sgyt_approval_status = True
        else:
            obj.sgyt_approval_status = False
        obj.sgyt_approver_name = str(user_name)
        obj.sgyt_approval_time = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        self.db_connection_obj.sess.commit()
        self.parent.refresh()

    def connect_to_log(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        data_obj = self.data_dict[obj_name]
        log_path = data_obj.sgyt_unix_path
        #now feteh the data from the path and print it
        encoded_string = return_encoded_log(DUG_connection_obj=self.DUG_connection_obj, log_path=log_path)
        ebcdic = return_ebcdic_from_sgyt(encoded_string.decode('base64'))
        title = log_path
        self.ebcdic_text_box = pop_up_text_box_view_only("", title)
        for i in range(0, 3201, 80):
            self.ebcdic_text_box.text_edit.append(ebcdic[i:i + 80])
        self.ebcdic_text_box.closed.connect(self.show)
        self.ebcdic_text_box.resize(800, 700)
        self.ebcdic_text_box.show()
        # print text_to_show

#-----------------------------------------------------------------------------------------------

class SEQG_SEGY_on_disk_QC(QtGui.QScrollArea):
    def __init__(self, parent):
        super(SEQG_SEGY_on_disk_QC, self).__init__()
        ts = time.time()
        self.parent = parent
        self.deliverable = self.parent.deliverable
        self.tool_tip_dict = tool_tips_mapper_dict['segy_tabs_2d']
        self.setToolTip(self.tool_tip_dict['on_disk'])
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.deliverable_id = self.parent.deliverable_id
        self.grid = QtGui.QGridLayout()
        self.widget = QtGui.QWidget()
        # add labels
        self.add_labels()
        self.add_data()
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)

        te = time.time()
        time_string = "{:8.5f} sec".format(te - ts)
        logger.info("Finished Creating SEGY on disk QC widget in: " + time_string)

    def add_labels(self):
        labels_list = ['Seq #', 'Line name', 'SEGYT QC','Export','Export status','Exported by', 'Time stamp','QC run status','Link', 'Header Extraction','Approve',
                       'Approval status', 'Approved by', 'Approval timestamp','Line name','Seq #']
        for i in range(0, len(labels_list)):
            self.grid.addWidget(create_central_labels(labels_list[i]), 0, i)

    def add_data(self):
        self.data_dir_entry = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables_data_dir).filter(
            self.db_connection_obj.Deliverables_data_dir.deliverable_id == self.deliverable_id).filter(
            self.db_connection_obj.Deliverables_data_dir.dir_type == 'data').first()
        self.dir_path = self.data_dir_entry.path
        # data = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable_id).order_by(
        #     self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc).all()
        data = get_data_for_SEGY_qc(self.db_connection_obj,self.deliverable_id)
        # now create a dictinoary for status
        data_dict = {}
        for obj in data:
            key = obj.line_name
            data = obj
            data_dict.update({key: data})
        self.data_dict = data_dict
        # Now search for all available lines that have been shot in orca line
        lines_shot = self.db_connection_obj.sess.query(self.db_connection_obj.Line).order_by(
            self.db_connection_obj.Line.sequence_number).all()
        line_name_list = []
        for aline in lines_shot:
            if int(aline.sequence_number) < 9000:
                line_name_list.append((aline.sequence_number, aline.real_line_name))
            else:
                pass
        #now fetch the directory content list
        cmd = str("ls " + self.dir_path)
        available_file_list = fetch_directory_content_list(self.DUG_connection_obj, cmd)
        available_file_dict = {}
        for a_line in line_name_list:
            a_line_name_segy = str(a_line[1] + '.sgy')
            if a_line_name_segy in available_file_list:
                available_file_dict.update({a_line[1]:True})
            else:
                available_file_dict.update({a_line[1]:False})

        # now add the objects in the line_name_list
        for i in range(1, len(line_name_list) + 1):
            # the 1st two and the last two columens
            self.grid.addWidget(create_center_data(str(line_name_list[i - 1][0])), i, 0)
            self.grid.addWidget(create_center_data(line_name_list[i - 1][1]), i, 1)
            self.grid.addWidget(create_center_data(str(line_name_list[i - 1][0])), i,15)
            self.grid.addWidget(create_center_data(line_name_list[i - 1][1]), i,14)
            # now check if some data exists for this in the data_dict
            if line_name_list[i - 1][1] in data_dict.keys():
                sgyt_data = data_dict[line_name_list[i - 1][1]]
                self.grid.addWidget(decide_and_create_label(sgyt_data.sgyt_approval_status),i,2) # add SGYT QC status
                if sgyt_data.sgyt_approval_status: # if SGYT approval status is not True do not proceed
                    pb_segy_exp = QtGui.QPushButton("Update")
                    pb_segy_exp.setObjectName(sgyt_data.line_name)
                    pb_segy_exp.setToolTip(posixpath.join(self.dir_path,str(sgyt_data.line_name+ '.sgy')))
                    pb_segy_exp.clicked.connect(self.show_export_upate_pop_up)
                    self.grid.addWidget(pb_segy_exp,i,3)
                    file_name = str(sgyt_data.line_name + '.sgy')
                    file_path = posixpath.join(self.dir_path, file_name)
                    status = available_file_dict[sgyt_data.line_name]
                    if status: # if the SEGYT file is on disk writing or finished, otherwise STOP
                        self.grid.addWidget(decide_and_create_label(sgyt_data.segy_disk_export_status), i, 4)
                        if sgyt_data.segy_disk_export_status is not None: # if the export status is set to true or false add exporter name and time stamp labels
                            self.grid.addWidget(create_center_data(sgyt_data.segy_exporter_name),i,5)
                            self.grid.addWidget(create_center_data(sgyt_data.segy_on_disk_time_stamp),i,6)
                            if sgyt_data.segy_disk_export_status: # Add the option to QC the file if the export is set to True
                                self.grid.addWidget(decide_and_create_label(sgyt_data.segy_on_disk_qc_run_status),i,7) # The run status should be update by SEGY on disk QC ops
                                if sgyt_data.segy_on_disk_qc_run_status: # if the run status is True add the button to approve log and link to the log,extractionstatus
                                    pb_connect_log = QtGui.QPushButton('View QC log')
                                    pb_connect_log.setObjectName(sgyt_data.segy_on_disk_qc_log_path)
                                    pb_connect_log.setToolTip(sgyt_data.segy_on_disk_qc_log_path)
                                    pb_connect_log.clicked.connect(self.show_QC_log)
                                    self.grid.addWidget(pb_connect_log,i,8)
                                    self.grid.addWidget(decide_and_create_label(sgyt_data.header_extraction_flag),i,9)
                                    if sgyt_data.header_extraction_flag: # if the extraction status is true, add approve button and qc status button
                                        pb_approve_log = QtGui.QPushButton('Approve')
                                        pb_approve_log.setObjectName(sgyt_data.segy_on_disk_qc_log_path)
                                        pb_approve_log.clicked.connect(self.show_approve_qc_log)
                                        self.grid.addWidget(pb_approve_log,i,10)
                                        self.grid.addWidget(decide_and_create_label(sgyt_data.segy_on_disk_qc_status),i,11)
                                        if sgyt_data.segy_on_disk_qc_status is not None: # Now add the time and name for approver
                                            self.grid.addWidget(create_center_data(sgyt_data.segy_on_disk_qc_approver_name),i,12)
                                            self.grid.addWidget(create_center_data(sgyt_data.segy_on_disk_qc_approval_time_stamp), i, 13)


    def show_QC_log(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        encoded_string = return_encoded_log(DUG_connection_obj=self.DUG_connection_obj, log_path=obj_name)
        log_data = encoded_string.decode('base64')
        title = obj_name
        self.log_viewer = SEGY_qc_log(self,log_data,title,self.deliverable.type)
        self.log_viewer.closed.connect(self.show)
        self.log_viewer.setMinimumWidth(1000)
        self.log_viewer.show()

    def show_export_upate_pop_up(self):
        sender = self.sender()
        self.obj_name = str(sender.objectName())
        # first check if the file exists in the directory
            #get the file path for the deliverable id data dir from the database
        file_name = str(self.obj_name + ".sgy")
        file_path = posixpath.join(self.dir_path,file_name)
        status = check_generic_path(self.DUG_connection_obj,file_path)
        if status == 'True':
            message = str("Found the file, Update the status for SEGY export for: " + file_path)
            self.approval_pop_up = pop_up_approval_box(message)
            self.approval_pop_up.closed.connect(self.update_segy_export)
            self.approval_pop_up.setMinimumWidth(400)
            self.approval_pop_up.show()
        else:
            message = str("Unable to find the file for: " + file_path)
            self.approval_pop_up = pop_up_message_box(message,'Critical')
            self.approval_pop_up.setMinimumWidth(300)
            self.approval_pop_up.show()

    def update_segy_export(self,user_name,status):
        obj = self.data_dict[self.obj_name]
        if status:
            obj.segy_disk_export_status = True
        else:
            obj.segy_disk_export_status = False
        obj.segy_exporter_name = str(user_name)
        file_name = str(self.obj_name + ".sgy")
        file_path = posixpath.join(self.dir_path, file_name)
        time_stamp = get_file_timestamp(self.DUG_connection_obj,file_path)
        obj.segy_on_disk_time_stamp = parser.parse(time_stamp[5].split(": ")[1]).strftime("%I:%M%p on %B %d, %Y")
        obj.segy_on_disk_file_path = file_path
        self.db_connection_obj.sess.commit()
        self.parent.refresh()


    def show_approve_qc_log(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        self.db_obj_update = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_qc_log_path == obj_name).first()
        self.SEGY_approve_form = approve_form_SEGY_on_disk_qc(self,self.deliverable.type)
        self.SEGY_approve_form.show()


    def approve_qc_log(self,name_to_use,status):
        self.db_obj_update.segy_on_disk_qc_status = status
        self.db_obj_update.segy_on_disk_qc_approver_name = str(name_to_use)
        self.db_obj_update.segy_on_disk_qc_approval_time_stamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        self.db_connection_obj.sess.commit()
        self.SEGY_approve_form.close()
        self.parent.refresh()


#-----------------------------------------------------------------------------------------------
class SEQG_SEGY_write_QC_status(QtGui.QScrollArea):
    def __init__(self, parent):
        super(SEQG_SEGY_write_QC_status, self).__init__()
        ts = time.time()
        self.parent = parent
        self.deliverable = self.parent.deliverable  # This is used to decide the number of tabs for SEGY write and summary

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj


        self.grid = QtGui.QGridLayout()

        SEGY_write_widget = SEGY_write_tabs(self)

        self.grid.addWidget(SEGY_write_widget,0,0)

        self.setLayout(self.grid)
        te = time.time()
        time_string = "{:8.5f} sec".format(te - ts)
        logger.info("Finished Creating SEGY write summary widget in: " + time_string)
        #self.show()


    def refresh_write_status(self):
        SEGY_write_widget = SEGY_write_tabs(self)
        self.grid.addWidget(SEGY_write_widget, 0, 0)
        self.setLayout(self.grid)

class SEGY_write_tabs(QtGui.QTabWidget):
    def __init__(self, parent):
        super(SEGY_write_tabs, self).__init__()
        self.parent = parent
        #Add the summary as this is always there
        SEGY_write_sumamry_widget = SEGY_write_sumamry(self.parent)
        self.addTab(SEGY_write_sumamry_widget,'Summary')
        for i in range(0,int(self.parent.deliverable.copies)): #this setps add a atab for every deliverable set defined in deliverables
            widget_name = str('Set no: ' + str(i+1))
            set_no = i+1
            widget_to_use = SEGY_write_set_details(self.parent,set_no)
            self.addTab(widget_to_use,widget_name)



class SEGY_write_sumamry(QtGui.QScrollArea):
    def __init__(self,parent):
        super(SEGY_write_sumamry,self).__init__()
        self.parent = parent
        self.deliverable = self.parent.deliverable
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.widget_to_use = QtGui.QWidget()
        self.grid = QtGui.QGridLayout()

        self.add_labels()
        self.add_data()

        self.widget_to_use.setLayout(self.grid)
        self.setWidget(self.widget_to_use)


    def add_labels(self):
        label_seq = ['Seq #','Line name','SEGY on disk QC']
        set_wise_label = ['Write status','QC status']
        set_label_start_column = 3
        for i in range(0,len(label_seq)):
            self.grid.addWidget(create_central_labels(label_seq[i]),1,i)
        for i in range(0,self.deliverable.copies):
            set_label = str('Set no: ' + str(i+1))
            set_label_start = i*2 + set_label_start_column
            self.grid.addWidget(create_central_labels(set_label),0,set_label_start,1,2)
            for j in range(0,len(set_wise_label)):
                self.grid.addWidget(create_central_labels(set_wise_label[j]),1,set_label_start+j)

    def add_data(self):
        set_start_column = 3
        data_segy_qc = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
            self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable.id).order_by(
            self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc).all()
        # valid SEGY QC id list for the case
        valid_segy_qc_list = []
        for item in data_segy_qc:
            valid_segy_qc_list.append(item.id_seq_segy_qc)
        # now create a dictinoary for status
        self.segy_ondisk_data_dict = {}
        for obj in data_segy_qc:
            if obj.segy_on_disk_qc_run_status:  # for all the objects in SEGY on disk QC we ony want the ones where SEGY on disk QC was run to distinguish between ready and True of False
                key = obj.line_name
                data = obj
                self.segy_ondisk_data_dict.update({key: data})
        # Now search for all available lines that have been shot in orca line
        lines_shot = self.db_connection_obj.sess.query(self.db_connection_obj.Line).order_by(
            self.db_connection_obj.Line.sequence_number).all()
        line_name_list = []
        for aline in lines_shot:
            if int(aline.sequence_number) < 9000:
                line_name_list.append((aline.sequence_number, aline.real_line_name))
            else:
                pass
        # creating the data for SEGY write
        data_segy_write = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).all()
        self.segy_write_obj_dict = {}
        for obj in data_segy_write:
            if obj.id_segy_qc in valid_segy_qc_list:
                self.segy_write_obj_dict.update({(obj.id_segy_qc,int(obj.set_number)): obj})

        #print self.segy_write_obj_dict

        # now add the objects
        for i in range(1, len(line_name_list) + 1):  # This needs to be added one more time
            self.grid.addWidget(create_center_data(str(line_name_list[i - 1][0])), i+1, 0)
            self.grid.addWidget(create_center_data(line_name_list[i - 1][1]), i+1, 1)
            if line_name_list[i - 1][1] in self.segy_ondisk_data_dict.keys():
                self.grid.addWidget(decide_and_create_label(
                    self.segy_ondisk_data_dict[line_name_list[i - 1][1]].segy_on_disk_qc_status), i+1, 2)
                segy_qc_id = self.segy_ondisk_data_dict[line_name_list[i - 1][1]].id_seq_segy_qc
                if self.segy_ondisk_data_dict[line_name_list[i - 1][1]].segy_on_disk_qc_status:
                    for j in range(0,self.deliverable.copies):
                        if (segy_qc_id,j+1) in self.segy_write_obj_dict.keys():
                            self.grid.addWidget(decide_and_create_label(self.segy_write_obj_dict[(segy_qc_id,j+1)].tape_write_status),
                                            i+1, (int(self.segy_write_obj_dict[(segy_qc_id,j+1)].set_number)-1)*2 + set_start_column)
                            if self.segy_write_obj_dict[(segy_qc_id,j+1)].tape_qc_run_status:  # If the tape qc was run
                                self.grid.addWidget(
                                    decide_and_create_label(self.segy_write_obj_dict[(segy_qc_id,j+1)].tape_qc_status), i+1 , (int(self.segy_write_obj_dict[(segy_qc_id,j+1)].set_number)-1)*2 + set_start_column+1)
                        else:
                                self.grid.addWidget(
                                    decide_and_create_label(""),
                                    i + 1, j*2+ set_start_column)


class SEGY_write_set_details(QtGui.QScrollArea):
    def __init__(self,parent,set_no):
        super(SEGY_write_set_details,self).__init__()
        self.parent = parent

        self.set_no = set_no
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.deliverable = self.parent.deliverable

        self.widget_to_use = QtGui.QWidget()
        self.grid = QtGui.QGridLayout()
        self.widget_to_use.setLayout(self.grid)

        self.add_labels()
        self.add_data()

        self.setWidget(self.widget_to_use)


    def add_labels(self):
        label_list = ['Tape #','Seq #', 'Line name','SEGY on disk QC', 'Tape write status',
                      'Tape written by','Tape written on','View and QC log','Tape QC status',
                      'Tape checked by', 'Tape checked on']
        for i in range(0,len(label_list)):
            self.grid.addWidget(create_central_labels(label_list[i]),0,i)


    def add_data(self):
        #Creating the data for SEGY QC for all entries for a particular deliverable
        data_segy_qc = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable.id).order_by(
            self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc).all()
        #valid SEGY QC id list for the case
        valid_segy_qc_list = []
        for item in data_segy_qc:
            valid_segy_qc_list.append(item.id_seq_segy_qc)
        # now create a dictinoary for status
        self.segy_ondisk_data_dict = {} # {linename : DAO for segy QC}
        for obj in data_segy_qc:
            if obj.segy_on_disk_qc_run_status: # for all the objects in SEGY on disk QC we ony want the ones where SEGY on disk QC was run to distinguish between ready and True of False
                key = obj.line_name
                data = obj
                self.segy_ondisk_data_dict.update({key: data})
        # Now search for all available lines that have been shot in orca line
        lines_shot = self.db_connection_obj.sess.query(self.db_connection_obj.Line).order_by(
            self.db_connection_obj.Line.sequence_number).all()
        line_name_list = []
        for aline in lines_shot:
            if int(aline.sequence_number) < 9000:
                line_name_list.append((aline.sequence_number, aline.real_line_name))
            else:
                pass
        # creating the data for SEGY write
        data_segy_write = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).filter(
            self.db_connection_obj.SEGY_write.set_number == self.set_no).all()
        self.segy_write_obj_dict_set_wise = {} # { SEGYQC_id : DAO for SEGY write}
        for obj in data_segy_write:
            if obj.id_segy_qc in valid_segy_qc_list:
                self.segy_write_obj_dict_set_wise.update({obj.id_segy_qc : obj})


        # now add the objects
        for i in range(1, len(line_name_list) + 1): # This needs to be added one more time
            self.grid.addWidget(create_center_data(str(line_name_list[i - 1][0])), i, 1)

            self.grid.addWidget(create_center_data(line_name_list[i - 1][1]), i, 2)

            if line_name_list[i-1][1] in self.segy_ondisk_data_dict.keys():
                self.grid.addWidget(decide_and_create_label(self.segy_ondisk_data_dict[line_name_list[i-1][1]].segy_on_disk_qc_status),i,3)
                segy_qc_id = self.segy_ondisk_data_dict[line_name_list[i-1][1]].id_seq_segy_qc
                if segy_qc_id in self.segy_write_obj_dict_set_wise.keys():
                    self.grid.addWidget(create_central_labels(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_label),i,0)
                    self.grid.addWidget(decide_and_create_label(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_write_status),i,4)
                    self.grid.addWidget(create_center_data(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_written_by),i,5)
                    self.grid.addWidget(create_center_data(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_written_on),i,6)
                    pb_view_log = QtGui.QPushButton('View log')
                    pb_view_log.setObjectName(str(segy_qc_id))
                    pb_view_log.clicked.connect(self.show_log)
                    self.grid.addWidget(pb_view_log,i,7)
                    if self.segy_write_obj_dict_set_wise[segy_qc_id].tape_qc_run_status: # If the tape qc was run
                        self.grid.addWidget(decide_and_create_label(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_qc_status),i,8)
                        self.grid.addWidget(create_center_data(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_checked_by),i,9)
                        self.grid.addWidget(create_center_data(self.segy_write_obj_dict_set_wise[segy_qc_id].tape_checked_on),i,10)
                else:
                    if self.segy_ondisk_data_dict[line_name_list[i-1][1]].segy_on_disk_qc_status:
                        self.grid.addWidget(decide_and_create_label(""),
                                        i, 3)

    def show_log(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        # print obj_name
        self.id_segy_qc = obj_name
        segy_w_log_path = self.segy_write_obj_dict_set_wise[int(obj_name)].segy_w_path
        self.segy_w_log_path = segy_w_log_path
        self.db_connection_obj.sess.flush()
        self.tape_write_obj_to_change = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).filter(
            self.db_connection_obj.SEGY_write.segy_w_path == segy_w_log_path).filter(
            self.db_connection_obj.SEGY_write.id_segy_qc == obj_name).first()
        logger.info("Now Fetching: " + segy_w_log_path)
        encoded_string = return_encoded_log(DUG_connection_obj=self.DUG_connection_obj, log_path=segy_w_log_path)
        message = encoded_string.decode('base64')
        self.pop_up_approval = pop_up_approval_box_segy_write(message=message)
        self.pop_up_approval.closed.connect(self.approve_log)
        self.pop_up_approval.approve_all.connect(self.approve_all_files_on_tape)
        self.pop_up_approval.setMinimumWidth(600)
        self.pop_up_approval.show()


    def approve_log(self,user_name,approval_status):
        tape_write_obj_to_change = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).filter(
            self.db_connection_obj.SEGY_write.segy_w_path == self.segy_w_log_path
        ).filter(
            self.db_connection_obj.SEGY_write.id_segy_qc == self.id_segy_qc
        ).first()
        if tape_write_obj_to_change.tape_qc_run_status is None:
            tape_write_obj_to_change.tape_qc_run_status = True
            tape_write_obj_to_change.tape_qc_status = approval_status
            tape_write_obj_to_change.tape_checked_by = str(user_name)
            tape_write_obj_to_change.tape_checked_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        else:
            file_name_dao = self.db_connection_obj.sess.query(
                self.db_connection_obj.SEGY_QC_on_disk).filter(
                self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc == tape_write_obj_to_change.id_segy_qc).first()
            message = str("Tape Label : " + tape_write_obj_to_change.tape_label + " set_no : " + str(tape_write_obj_to_change.set_number) + ' linename : ' + file_name_dao.line_name + 'The log was checked before by: ' + tape_write_obj_to_change.tape_checked_by + " on: " + tape_write_obj_to_change.tape_checked_on + ' ,please enter the reason to change')
            status = change_log_creation(gui=self,conn_obj=self.db_connection_obj,message=message,type_entry='change',location = 'segy_write')
            if status:
                self.tape_write_obj_to_change.tape_qc_status = approval_status
                self.tape_write_obj_to_change.tape_checked_by = str(user_name)
                self.tape_write_obj_to_change.tape_checked_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        self.db_connection_obj.sess.commit()
        # Now create the media list object if necessary ie only if the approval status is True
        # if approval_status:
        #     if (self.deliverable.type, self.deliverable.media) in SEGY_write_to_media_table_list: # only if the media entry needs to be created from here
        #         self.check_and_create_media_list_entry()


    def approve_all_files_on_tape(self,user_name, approval_status):
        """
        get all the segy files written to tape and loop through them to approve them one at a time, prompt for message if the file was approved before

        :param user_name: user name approving the file
        :param approval_status: True or false if this function is called
        :return: none

        """

        dao_list_tape = self.db_connection_obj.sess.query(
            self.db_connection_obj.SEGY_write).filter(
            self.db_connection_obj.SEGY_write.segy_w_path == self.segy_w_log_path).all()

        for tape_write_obj_to_change in dao_list_tape:
            file_name_dao = self.db_connection_obj.sess.query(
                self.db_connection_obj.SEGY_QC_on_disk).filter(
                self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc == tape_write_obj_to_change.id_segy_qc).first()
            if tape_write_obj_to_change.tape_qc_run_status is None:
                logger.info("Now Approving SEGY write => Tape Label : " +  tape_write_obj_to_change.tape_label + " set_no : " + str(tape_write_obj_to_change.set_number) + ' linename : ' + file_name_dao.line_name )
                tape_write_obj_to_change.tape_qc_run_status = True
                tape_write_obj_to_change.tape_qc_status = approval_status
                tape_write_obj_to_change.tape_checked_by = str(user_name)
                tape_write_obj_to_change.tape_checked_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            else:
                logger.warning("Db entry exists for  => Tape Label : " + tape_write_obj_to_change.tape_label + " set_no : " + str(tape_write_obj_to_change.set_number) + ' linename : ' + file_name_dao.line_name)
                message = str("Tape Label : " + tape_write_obj_to_change.tape_label + " set_no : " + str(tape_write_obj_to_change.set_number) + ' linename : ' + file_name_dao.line_name  + 'The log was checked before by: ' + tape_write_obj_to_change.tape_checked_by +  " on: " + tape_write_obj_to_change.tape_checked_on + ' ,please enter the reason to change')
                status = change_log_creation(gui=self,conn_obj=self.db_connection_obj,message=message,type_entry='change',location = 'segy_write')
                if status:
                    tape_write_obj_to_change.tape_qc_status = approval_status
                    tape_write_obj_to_change.tape_checked_by = str(user_name)
                    tape_write_obj_to_change.tape_checked_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            self.db_connection_obj.sess.commit()


    def check_and_create_media_list_entry(self):
        # How to decide the deliverable and set no + reel no
        segy_qc_obj = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
            self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc == self.tape_write_obj_to_change.id_segy_qc
        ).first()
        reel_no = segy_qc_obj.sgyt_reel_no
        #1st check if the particular entry exists in media list
        db_obj_list = self.db_connection_obj.sess.query(self.db_connection_obj.Media_list).filter(
            self.db_connection_obj.Media_list.deliverable_id == self.deliverable.id
        ).filter(self.db_connection_obj.Media_list.set_no == self.set_no ).filter(self.db_connection_obj.Media_list.reel_no == reel_no).all()
        if len(db_obj_list) == 0: # No previous entry exists in DB, simply create a new one
            new_media_list_obj = self.db_connection_obj.Media_list()
            new_media_list_obj.deliverable_id = self.deliverable.id
            new_media_list_obj.set_no = self.set_no
            new_media_list_obj.media_label = reel_no
            new_media_list_obj.use_tag = True
            new_media_list_obj.reel_no = reel_no
            self.db_connection_obj.sess.add(new_media_list_obj)
            self.db_connection_obj.sess.commit()
        else:
            for obj in db_obj_list:
                if obj.use_tag == True:
                    message = str("Media list entry exists before, press y to set the last entry as False and the new one as True")
                    status = get_item_through_dialogue(self, message)
                    if status == 'y':
                        obj.use_tag = False
            new_media_list_obj = self.db_connection_obj.Media_list()
            new_media_list_obj.deliverable_id = self.deliverable.id
            new_media_list_obj.set_no = self.set_no
            new_media_list_obj.media_label = reel_no
            new_media_list_obj.use_tag = True
            new_media_list_obj.reel_no = reel_no
            self.db_connection_obj.sess.add(new_media_list_obj)
            self.db_connection_obj.sess.commit()



