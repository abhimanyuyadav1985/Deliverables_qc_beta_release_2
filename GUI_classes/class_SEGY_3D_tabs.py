from PyQt4 import QtGui
from general_functions.general_functions import create_central_labels,create_center_data,decide_and_create_label,change_log_creation
from dug_ops.segy_templ import return_ebcdic_from_sgyt
from class_pop_up_message_box import pop_up_message_box,pop_up_approval_box
from dug_ops.DUG_ops import return_encoded_log
from class_pop_up_text_box import pop_up_text_box_view_only
import datetime
from dateutil import parser
from dug_ops.DUG_ops import check_generic_path, get_file_timestamp
import posixpath
from class_SEGY_log import SEGY_qc_log, approve_form_SEGY_on_disk_qc
from configuration import SEGY_write_to_media_table_list
from general_functions.general_functions import get_item_through_dialogue

class SEGY_3D_status_tabs(QtGui.QTabWidget):
    def __init__(self, parent):
        super(SEGY_3D_status_tabs, self).__init__()
        self.parent = parent
        self.tab1 = SEGY_3D_SGYT_status(self.parent)
        self.tab2 = SEGY_3D_on_disk_QC(self.parent)
        self.tab3 = SEGY_3D_write_QC_status(self.parent)
        self.addTab(self.tab1, "SGYT")
        self.addTab(self.tab2, "On disk")
        self.addTab(self.tab3, "Write QC")

        #----------------------------------------------

class SEGY_3D_SGYT_status(QtGui.QScrollArea):

    def __init__(self, parent):
        super(SEGY_3D_SGYT_status, self).__init__()
        self.parent = parent

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.deliverable = self.parent.deliverable
        self.deliverable_id = self.parent.deliverable_id

        self.grid = QtGui.QGridLayout()

        # add labels
        self.add_labels()
        self.add_data()
        self.widget = QtGui.QWidget()
        self.widget.setLayout(self.grid)
        self.setWidget(self.widget)
        #self.show()


    def add_labels(self):
        labels_list  = ['Name','SGYT export','SGYT reel_no','Exported by','Date','SGYT view','Approve','Approval status','Approved by','Approval timestamp']
        for i in range(0,len(labels_list)):
            self.grid.addWidget(create_central_labels(labels_list[i]),0,i)

    def add_data(self):
        sgyt_data = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
            self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable_id).first()
        self.grid.addWidget(create_center_data(str(self.deliverable.name)), 1, 0)
        if sgyt_data is not None:
            self.data_dict = {self.deliverable.name : sgyt_data}
            self.grid.addWidget(decide_and_create_label(str(sgyt_data.sgyt_status)),1,1)
            self.grid.addWidget(create_center_data(sgyt_data.sgyt_reel_no),1,2)
            self.grid.addWidget(create_center_data(sgyt_data.sgyt_exp_uname),1,3)
            self.grid.addWidget(create_center_data(sgyt_data.sgyt_time_stamp),1,4)
            # now add push button to view log
            pb = QtGui.QPushButton("view SGYT")
            pb.setObjectName(str(self.deliverable.name))
            pb.clicked.connect(self.connect_to_log)
            self.grid.addWidget(pb,1,5)
            self.grid.addWidget(decide_and_create_label(sgyt_data.sgyt_approval_status),1,7) # this will automatically decide and create the necessary label True false or blank
            # pb to approve the log
            pb_approval = QtGui.QPushButton("Approve")
            pb_approval.setObjectName(self.deliverable.name)
            pb_approval.clicked.connect(self.show_approval_popup)
            self.grid.addWidget(pb_approval,1,6)
            #now check and add aprrover name it the approval status is not blank
            if sgyt_data.sgyt_approval_status is not None:
                self.grid.addWidget(create_center_data(sgyt_data.sgyt_approver_name), 1, 8)
                self.grid.addWidget(create_center_data(sgyt_data.sgyt_approval_time), 1, 9)
        else:
            self.grid.addWidget(decide_and_create_label(""), 1, 2)

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

class SEGY_3D_on_disk_QC(QtGui.QScrollArea):
    def __init__(self, parent):
        super(SEGY_3D_on_disk_QC, self).__init__()
        self.parent = parent
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

    def add_labels(self):
        labels_list = ['Name', 'SEGYT QC','Export','Export status','Exported by', 'Time stamp','QC run status','Link', 'Header Extraction','Approve',
                       'Approval status', 'Approved by', 'Approval timestamp','Name']
        for i in range(0, len(labels_list)):
            self.grid.addWidget(create_central_labels(labels_list[i]), 0, i)

    def add_data(self):
        self.data_dir_entry = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables_data_dir).filter(
            self.db_connection_obj.Deliverables_data_dir.deliverable_id == self.deliverable_id).filter(
            self.db_connection_obj.Deliverables_data_dir.dir_type == 'data').first()
        self.dir_path = self.data_dir_entry.path
        sgyt_data = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
        self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable_id).first()
        self.data_dict = {self.deliverable.name : sgyt_data}
        self.grid.addWidget(create_center_data(self.deliverable.name), 1, 0)
        self.grid.addWidget(create_center_data(self.deliverable.name), 1, 13)
        self.grid.addWidget(decide_and_create_label(sgyt_data.sgyt_approval_status),1,1)
        if sgyt_data.sgyt_approval_status: # if SGYT approval status is not True do not proceed
                pb_segy_exp = QtGui.QPushButton("Update")
                pb_segy_exp.setObjectName(self.deliverable.name)
                pb_segy_exp.clicked.connect(self.show_export_upate_pop_up)
                self.grid.addWidget(pb_segy_exp,1,2)
                file_name = str(self.deliverable.name + '.sgy')
                file_path = posixpath.join(self.dir_path, file_name)
                status = check_generic_path(self.DUG_connection_obj, file_path)
                if status == 'True': # if the SEGYT file is on disk writing or finished, otherwise STOP
                    self.grid.addWidget(decide_and_create_label(sgyt_data.segy_disk_export_status), 1, 3)
                    if sgyt_data.segy_disk_export_status is not None: # if the export status is set to true or false add exporter name and time stamp labels
                        self.grid.addWidget(create_center_data(sgyt_data.segy_exporter_name),1,4)
                        self.grid.addWidget(create_center_data(sgyt_data.segy_on_disk_time_stamp),1,5)
                        if sgyt_data.segy_disk_export_status: # Add the option to QC the file if the export is set to True
                            self.grid.addWidget(decide_and_create_label(sgyt_data.segy_on_disk_qc_run_status),1,6) # The run status should be update by SEGY on disk QC ops
                            if sgyt_data.segy_on_disk_qc_run_status: # if the run status is True add the button to approve log and link to the log,extractionstatus
                                pb_connect_log = QtGui.QPushButton('View QC log')
                                pb_connect_log.setObjectName(sgyt_data.segy_on_disk_qc_log_path)
                                pb_connect_log.clicked.connect(self.show_QC_log)
                                self.grid.addWidget(pb_connect_log,1,7)
                                self.grid.addWidget(decide_and_create_label(sgyt_data.header_extraction_flag),1,8)
                                if sgyt_data.header_extraction_flag: # if the extraction status is true, add approve button and qc status button
                                    pb_approve_log = QtGui.QPushButton('Approve')
                                    pb_approve_log.setObjectName(sgyt_data.segy_on_disk_qc_log_path)
                                    pb_approve_log.clicked.connect(self.show_approve_qc_log)
                                    self.grid.addWidget(pb_approve_log,1,9)
                                    self.grid.addWidget(decide_and_create_label(sgyt_data.segy_on_disk_qc_status),1,10)
                                    if sgyt_data.segy_on_disk_qc_status is not None: # Now add the time and name for approver
                                        self.grid.addWidget(create_center_data(sgyt_data.segy_on_disk_qc_approver_name),1,11)
                                        self.grid.addWidget(create_center_data(sgyt_data.segy_on_disk_qc_approval_time_stamp), 1, 12)


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
            self.approval_pop_up = pop_up_message_box(self,message,'Critical')
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
class SEGY_3D_write_QC_status(QtGui.QScrollArea):
    def __init__(self, parent):
        super(SEGY_3D_write_QC_status, self).__init__()
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
        label_list = ['Set #','SEGY on disk QC status','Tape write status','Tape written by','Tape written on','View and Approve','Tape QC status','Tape checked by','Tape checked on']
        for i in range(0,len(label_list)):
            self.grid.addWidget(create_central_labels(label_list[i]),0,i)


    def add_data(self):
        # search the SEGY on disk QC table to check if the SEGY file for this deliverable
        self.segy_on_disk_qc_obj = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.deliverable.id).first()
        if self.segy_on_disk_qc_obj is not None:
            obj_id = self.segy_on_disk_qc_obj.id_seq_segy_qc
            #Now serach for the items in tape write log with the ID corresponding to this id
            self.segy_write_obj_list = self.db_connection_obj.sess.query(
                self.db_connection_obj.SEGY_write
            ).filter(self.db_connection_obj.SEGY_write.id_segy_qc == obj_id).all()
            self.segy_write_obj_dict = {}
            if len(self.segy_write_obj_list) != 0:
                for obj in self.segy_write_obj_list:
                    self.segy_write_obj_dict.update({obj.set_number : obj})
                # now add data
            for i in range(0,self.deliverable.copies):
                self.grid.addWidget(create_center_data(str('Set no: ' + str(i+1))),i+1,0)
                self.grid.addWidget(decide_and_create_label(self.segy_on_disk_qc_obj.segy_on_disk_qc_status),i+1,1)
                if i+1 in self.segy_write_obj_dict.keys():
                    if self.segy_on_disk_qc_obj.segy_on_disk_qc_status:
                        self.grid.addWidget(decide_and_create_label(self.segy_write_obj_dict[i+1].tape_write_status),i+1,2)
                        if self.segy_write_obj_dict[i + 1].tape_write_status:
                            self.grid.addWidget(create_center_data(self.segy_write_obj_dict[i + 1].tape_written_by),i+1,3)
                            self.grid.addWidget(create_center_data(self.segy_write_obj_dict[i + 1].tape_written_on),i+1,4)
                            pb_approve_log = QtGui.QPushButton('View log')
                            pb_approve_log.setObjectName(self.segy_write_obj_dict[i + 1].segy_w_path)
                            pb_approve_log.clicked.connect(self.show_log)
                            self.grid.addWidget(pb_approve_log,i+1,5)
                            if self.segy_write_obj_dict[i + 1].tape_qc_run_status:
                                self.grid.addWidget(decide_and_create_label(self.segy_write_obj_dict[i + 1].tape_qc_status),i+1,6)
                                self.grid.addWidget(create_center_data(self.segy_write_obj_dict[i + 1].tape_checked_by),i+1,7)
                                self.grid.addWidget(create_center_data(self.segy_write_obj_dict[i + 1].tape_checked_on),
                                                    i + 1, 8)
    def show_log(self):
        sender = self.sender()
        obj_name = str(sender.objectName())
        self.db_connection_obj.sess.flush()
        self.tape_write_obj_to_change = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).filter(
            self.db_connection_obj.SEGY_write.segy_w_path == obj_name).first()
        encoded_string = return_encoded_log(DUG_connection_obj=self.DUG_connection_obj, log_path=obj_name)
        message = encoded_string.decode('base64')
        self.pop_up_approval = pop_up_approval_box(message=message)
        self.pop_up_approval.closed.connect(self.approve_log)
        self.pop_up_approval.show()

    def approve_log(self, user_name, approval_status):
        if self.tape_write_obj_to_change.tape_qc_run_status is None:
            self.tape_write_obj_to_change.tape_qc_run_status = True
            self.tape_write_obj_to_change.tape_qc_status = approval_status
            self.tape_write_obj_to_change.tape_checked_by = str(user_name)
            self.tape_write_obj_to_change.tape_checked_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        else:
            message = str(
                'The log was checked before by: ' + self.tape_write_obj_to_change.tape_checked_by + " on: " + self.tape_write_obj_to_change.tape_checked_on + ' ,please enter the reason to change')
            status = change_log_creation(gui=self, conn_obj=self.db_connection_obj, message=message,
                                         type_entry='change', location='segy_write')
            if status:
                self.tape_write_obj_to_change.tape_qc_status = approval_status
                self.tape_write_obj_to_change.tape_checked_by = str(user_name)
                self.tape_write_obj_to_change.tape_checked_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        self.db_connection_obj.sess.commit()
        if approval_status:
            if (self.deliverable.type,
                self.deliverable.media) in SEGY_write_to_media_table_list:  # only if the media entry needs to be created from here
                self.check_and_create_media_list_entry()

    def check_and_create_media_list_entry(self):
        # How to decide the deliverable and set no + reel no
        segy_qc_obj = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
            self.db_connection_obj.SEGY_QC_on_disk.id_seq_segy_qc == self.tape_write_obj_to_change.id_segy_qc
        ).first()
        reel_no = segy_qc_obj.sgyt_reel_no
        # 1st check if the particular entry exists in media list
        db_obj_list = self.db_connection_obj.sess.query(self.db_connection_obj.Media_list).filter(
            self.db_connection_obj.Media_list.deliverable_id == self.deliverable.id
        ).filter(self.db_connection_obj.Media_list.set_no == self.set_no).filter(
            self.db_connection_obj.Media_list.reel_no == reel_no).all()
        if len(db_obj_list) == 0:  # No previous entry exists in DB, simply create a new one
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
                    message = str(
                        "Media list entry exists before, press y to set the last entry as False and the new one as True")
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






