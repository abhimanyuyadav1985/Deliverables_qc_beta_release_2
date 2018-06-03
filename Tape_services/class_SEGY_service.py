import os
from database_engine.DB_ops import get_list_of_SEGY_deliverables
from GUI_classes.class_pop_up_combo_box import pop_up_combo_box
from GUI_classes.class_pop_up_message_box import pop_up_message_box
from general_functions.class_deliverables_dir_service_through_db import deliverable_dir_service_through_db
from general_functions.class_deliverables_file_service import deliverable_file_service
from database_engine.DB_ops import get_all_production_sequences, get_all_SEGY_qc_objects, get_all_SEGY_write_objects
from dug_ops.segy_templ import create_sgyt,create_3D_sgyt
from general_functions.general_functions import get_item_through_dialogue
import posixpath
from dug_ops.DUG_ops import check_generic_path, SFTP_generic_file
from dug_ops.DUG_ops import fetch_directory_content_list, append_register_entry
from general_functions.general_functions import change_log_creation
import datetime
from configuration import use_mode,get_segy_write_script,sequence_wise_SEGY, SEGY_3D
from dug_ops.DUG_ops import append_register_entry
from GUI_classes.class_SEGY_QC_form import SEGY_QC_Form


import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class SEGY_service(object):
    
    def __init__(self,parent,**kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.parent = parent
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj
        self.name = "SEGY service"
        self.dir_service = deliverable_dir_service_through_db(self)
        self.file_service = deliverable_file_service(self)
        self.segy_write_script = get_segy_write_script()
        logger.info("SEGY Write Script: " + self.segy_write_script)


    def run(self):
        self.SEGY_path = ''
        for a_path in self.path_list:
            self.SEGY_path = self.SEGY_path + " " + a_path
        run_cmd = str("nohup " + self.segy_write_script + " tape=/dev/" + str(self.parent.tape_drive)+ self.SEGY_path + " > " + self.log_path + ' 2>&1 &')
        logger.info("Command to be executed : " + run_cmd)
        if use_mode == 'Demo':
            logger.warning("Running in DEMO mode command will only be printed not executed ....")
        elif use_mode == 'Production':
            segd_qc_register_obj = [run_cmd, self.parent.tape_drive, self.log_path, 'segy_w']
            logger.info("Now adding the SEGY write task to buffers ..")
            append_register_entry(self.DUG_connection_obj, segd_qc_register_obj)

    def create_qc_obj_dict(self):
        #This function creates a list of all the segy qc id for the files that will be written to the tape
        self.qc_obj_dict = {}
        for a_path in self.path_list:
            segy_qc_obj = self.db_connection_obj.sess.query(
                self.db_connection_obj.SEGY_QC_on_disk).filter(
                self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_file_path == a_path).first()
            key = segy_qc_obj.id_seq_segy_qc
            self.qc_obj_dict.update({key: segy_qc_obj})


    def create_write_object_list(self):
        self.existing_write_segy_qc_id_list = []
        self.existing_write_obj_dict = {}
        #This function is used to return all the segy write objects in the table for the selected sequences and set no
        self.segy_write_obj_list = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).filter(
            self.db_connection_obj.SEGY_write.id_segy_qc.in_(self.qc_obj_dict.keys())).filter(
            self.db_connection_obj.SEGY_write.set_number == int(self.parent.set_no)).all()
        if self.segy_write_obj_list == None:
            self.segy_write_obj_list = []
        for a_existing_write_obj in self.segy_write_obj_list:
            self.existing_write_segy_qc_id_list.append(a_existing_write_obj.id_segy_qc)
            self.existing_write_obj_dict.update({a_existing_write_obj.id_segy_qc:a_existing_write_obj })


    def chk_and_run(self):
        run_status = True
        self.create_qc_obj_dict() # This creates a dictionary with all the segy_path to be written to tape as key and segy_qc_obj as key
        self.create_write_object_list() # creates two attributes for self 1. a list of all the write obj and list of segy_qc_id in it
        self.username = self.get_user_name() # This username will be used for all the segy write obj entires
        for segy_qc_id in self.qc_obj_dict.keys():
            if segy_qc_id not in self.existing_write_segy_qc_id_list: # create a new write object
                self.save_as_segy_write_obj(segy_qc_id)
            else:
                segy_write_obj = self.existing_write_obj_dict[segy_qc_id]
                message = str("The segy file: " + self.qc_obj_dict[segy_qc_id].segy_on_disk_file_path +  " was tape was written before on Tape: " + segy_write_obj.tape_label +  " by : " + segy_write_obj.tape_written_by + " on : " + segy_write_obj.tape_written_on + ", Please enter the reason to re create.")
                change_log_status = change_log_creation(gui=self.parent.parent,conn_obj=self.db_connection_obj,message=message,type_entry="change",location = 'segy_write')
                if change_log_status:
                    segy_write_obj = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_write).filter(
                        self.db_connection_obj.SEGY_write.id_segy_qc == segy_qc_id).filter(
                        self.db_connection_obj.SEGY_write.set_number == int(self.parent.set_no)).first()
                    self.username = self.get_user_name()
                    segy_write_obj.tape_written_by = self.username
                    segy_write_obj.tape_written_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
                    #Set the other attributes to none as this is a new write
                    segy_write_obj.tape_label = self.tape_name
                    segy_write_obj.tape_qc_run_status = None
                    segy_write_obj.tape_sgy_name = None
                    segy_write_obj.tape_qc_status = None
                    segy_write_obj.tape_checked_by = None
                    segy_write_obj.tape_checked_on = None
                    segy_write_obj.segy_w_path = self.log_path
                    self.db_connection_obj.sess.commit()
                else:
                    run_status = False
        if run_status == True:
            self.run()

    def save_as_segy_write_obj(self, id_segy_qc_obj):
        new_obj = self.db_connection_obj.SEGY_write()
        new_obj.id_segy_qc = id_segy_qc_obj
        new_obj.tape_write_status  = True
        new_obj.tape_written_by = self.username
        new_obj.set_number = self.parent.set_no
        new_obj.tape_written_on = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        new_obj.segy_w_path = self.log_path
        new_obj.tape_label = self.tape_name
        self.db_connection_obj.sess.add(new_obj)
        self.db_connection_obj.sess.commit()

    def get_list_of_SEGY_files_in_dir(self):
        dir_path = self.parent.dir_service.data_dir_path_dict['data']
        cmd = str("ls " + dir_path)
        dir_list_for_combo = fetch_directory_content_list(self.parent.DUG_connection_obj, cmd)
        return dir_list_for_combo

    def get_list_of_files_where_ondisk_qc_is_approved(self):
        dir_path = self.parent.dir_service.data_dir_path_dict['data']
        cmd = str("ls " + dir_path)
        available_file_list = fetch_directory_content_list(self.parent.DUG_connection_obj, cmd)
        combo_list_for_tape_write = []
        approved_db_obj_list = []
        self.approved_obj_dict = {}
        temp_dict = {}
        # Now check how many of these files have SEGY_QC_approved
        db_obj_list = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).all()
        file_size_dict = {}
        for a_obj in db_obj_list:
            if a_obj.segy_on_disk_qc_status == True:
                approved_db_obj_list.append(a_obj.segy_on_disk_file_path)
                key = a_obj.segy_on_disk_file_path
                data = a_obj
                temp_dict.update({key:data})
        for a_segy in available_file_list:
            a_segy_path = posixpath.join(dir_path,a_segy)
            if a_segy_path in approved_db_obj_list:
                combo_list_for_tape_write.append(a_segy)
                size_for_file = temp_dict[a_segy_path].file_size
                file_size_dict.update({a_segy: size_for_file})
                self.approved_obj_dict.update({a_segy:temp_dict[a_segy_path]})
        return (combo_list_for_tape_write, file_size_dict)


    def remove_files_written_to_tape(self,file_list):
        """
        check with the database to get the SEGy QC id for the file and move to segy write file to check if the file is writeen to tape before for
        the particular set

        :param file_list:
        :return: removed file list with only the files that have not been writteen to the tape before
        """
        file_list_removed = []

        dir_path = self.parent.dir_service.data_dir_path_dict['data']

        segy_write_dao_list = get_all_SEGY_write_objects(self.parent.db_connection_obj)
        segy_qc_dao_list = get_all_SEGY_qc_objects(self.parent.db_connection_obj, self.parent.deliverable.id)

        # convert the dao lists to dictionary that we will use
        write_dao_dict = {}
        for a_write_dao in segy_write_dao_list:
            qc_id = a_write_dao.id_segy_qc
            if str(a_write_dao.set_number) == str(self.parent.set_no):
                write_dao_dict.update({qc_id : a_write_dao.tape_write_status})

        file_path_write_dict = {}
        for a_qc_dao in segy_qc_dao_list:
            file_path = a_qc_dao.segy_on_disk_file_path
            if a_qc_dao.id_seq_segy_qc in write_dao_dict.keys():
                tape_write_status = write_dao_dict[a_qc_dao.id_seq_segy_qc]
                file_path_write_dict.update({file_path : tape_write_status})
            else:
                file_path_write_dict.update({file_path: False})


        for a_file in file_list:
            a_file_path = posixpath.join(dir_path,a_file)
            if file_path_write_dict[a_file_path] == True:
                pass
            else:
                file_list_removed.append(a_file)

        return file_list_removed



    def set_SEGY_path_multiple(self, file_list):
        self.path_list = []
        for a_file in file_list:
            self.path_list.append(posixpath.join(self.parent.dir_service.data_dir_path_dict['data'],a_file))

    def set_SEGY_path(self,file_name):
        self.file_name = file_name
        self.SEGY_path = posixpath.join(self.parent.dir_service.data_dir_path_dict['data'],self.file_name)

    def set_logpath(self):
        log_name = self.tape_name + "-" + self.parent.set_no + ".rwlog"
        #print self.parent.dir_service.qc_dir_path_dict
        temp_dict = self.parent.dir_service.qc_dir_path_dict[int(self.parent.set_no)]
        #print temp_dict
        log_dir = temp_dict['write_log']
        self.log_path = posixpath.join(log_dir,log_name)

    def set_tape_name(self,tape_name):
        self.tape_name = tape_name


    def form_definition_for_SEGY_QC(self):
        SEGY_deliverables_list = get_list_of_SEGY_deliverables(self.db_connection_obj)
        disp_name_dict = {}
        combo_item_list = []
        for deliverable in SEGY_deliverables_list:
            key = str(deliverable.id) + "_" + deliverable.name
            data = deliverable
            disp_name_dict.update({key: data})
            combo_item_list.append(key)
        self.disp_name_dict = disp_name_dict
        return combo_item_list

    def form_definition_for_SEGY_QC_file(self):
        dir_path = self.dir_service.data_dir_path_dict['data']
        print dir_path
        cmd = str("ls " + dir_path)
        file_list = fetch_directory_content_list(self.DUG_connection_obj, cmd)
        file_path_dict = {}
        for file_name in file_list:
            file_path_dict.update({posixpath.join(dir_path, file_name): file_name})
        file_list_show = []  # if the SEGY export status is marked as true than only QC otherwise not
        db_result = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.segy_disk_export_status == True).all()
        db_result_dict = {}
        for item in db_result:
            db_result_dict.update({item.segy_on_disk_file_path:item})
          # This will be used to compare
        for item in file_path_dict.keys():
            if item in db_result_dict.keys():
                file_list_show.append(file_path_dict[item])
        return file_list_show


    def choose_deliverable(self,option):
        SEGY_deliverables_list = get_list_of_SEGY_deliverables(self.db_connection_obj)
        disp_name_dict = {}
        combo_item_list = []
        for deliverable in SEGY_deliverables_list:
            key = str(deliverable.id) + "_" + deliverable.name
            data = deliverable
            disp_name_dict.update({key: data})
            combo_item_list.append(key)

        self.disp_name_dict = disp_name_dict
        self.pop_up_combo_box = pop_up_combo_box(self, "Select deliverable", combo_item_list, 'Deliverable',option)
        self.pop_up_combo_box.show()

    def choose_sequence(self,option):
        seq_list = get_all_production_sequences(self.db_connection_obj)
        disp_name_dict = {}
        combo_item_list = []
        for seq in seq_list:
            key = str(seq.real_line_name)
            data = seq
            disp_name_dict.update({key: data})
            combo_item_list.append(key)
        self.disp_seq_dict = disp_name_dict
        self.pop_up_combo_box = pop_up_combo_box(self, "Select Sequence", combo_item_list, 'Sequence',option)
        self.pop_up_combo_box.show()


    def get_user_name(self):
        username = get_item_through_dialogue(self.parent.parent, 'Type username or exit to exit')
        if len(username) == 0:
            message = "Plese enter a valid username!"
            self.pop_up_message_box = pop_up_message_box(message=message,type = "Critical")
            self.pop_up_message_box.closed.connect(self.get_user_name)
            self.pop_up_message_box.show()
        else:
            return username


    def set_attribute(self, attribute, caller,ops):
        if ops == 'SGYT':
            if caller == 'Deliverable':
                self.Deliverable = self.disp_name_dict[attribute]
                #Check if the deliverable is of the type sequence wise
                if self.Deliverable.type in sequence_wise_SEGY:
                    #Now check if DUG SGYT master is defined for the deliverable
                    if self.Deliverable.sgyt_master_status:
                        #print self.Deliverable.sgyt.decode('base64')
                        self.choose_sequence(ops)
                    else:
                        logger.warning("No SGYT found for the deliverable in the database !!!")
                elif self.Deliverable.type in SEGY_3D:
                    if self.Deliverable.sgyt_master_status:
                        mnIL = get_item_through_dialogue(self.parent, 'Minimum IL')
                        mxIL = get_item_through_dialogue(self.parent, 'Maximum IL')
                        mnXL = get_item_through_dialogue(self.parent, 'Minimum XL')
                        mxXL = get_item_through_dialogue(self.parent, 'Maximum XL')
                        reel = get_item_through_dialogue(self.parent, 'Tape number excluding prefix')
                        self.reel = str('{0:04d}'.format(int(reel)))
                        self.IL_range = [mnIL, mxIL]
                        self.XL_range = [mnXL, mxXL]
                        username = self.get_user_name()
                        if username == 'exit':
                            pass
                        else:
                            if len(username) != 0:
                                self.username = username
                                self.create_SEGY_3D_sgyt()
                            else:
                                self.get_user_name()
                    else:
                        logger.warning("No SGYT found for the deliverable in the database !!!")
            elif caller == 'Sequence':
                self.sequence = self.disp_seq_dict[attribute]
                # get min max IL and XL ranges
                mnIL = get_item_through_dialogue(self.parent,'Minimum IL')
                mxIL = get_item_through_dialogue(self.parent,'Maximum IL')
                mnXL = get_item_through_dialogue(self.parent, 'Minimum XL')
                mxXL = get_item_through_dialogue(self.parent, 'Maximum XL')
                reel = get_item_through_dialogue(self.parent, 'Tape number excluding prefix')
                self.reel = str('{0:04d}'.format(int(reel)))
                self.IL_range = [mnIL,mxIL]
                self.XL_range = [mnXL,mxXL]
                username = self.get_user_name()
                if username == 'exit':
                    pass
                else:
                    if len(username) !=0:
                        self.username = username
                        self.create_sequence_wise_sgyt()
                    else:
                        self.get_user_name()
        elif ops == 'per_QC':
            if caller == 'Deliverable':
                self.Deliverable = self.disp_name_dict[attribute]
                #Now check if the bin def and trc def file exists for the deliverable
                if self.Deliverable.bin_def_status and self.Deliverable.trc_def_status:
                    # now the deliverable is set, time to set the dir service to the deliverable
                    self.dir_service.set_deliverable(self.Deliverable)
                    # return the list of SEGY files for the deliverable in the large files+ deliverable dir
                    self.choose_sgy_file_for_QC(ops)
                else:
                    logger.warning("The bin.def and trc.def files for the deliberable are not defined in the database!!!")
            if caller == 'file_sgy':
                #fetch the bin def and trc def files from the database and create files in temp dir and SFTP them to the DUG WS
                (bin_def_path, trc_def_path) = self.create_def_files_and_sFTP()
                file_path = posixpath.join(self.dir_service.data_dir_path_dict['data'],attribute)
                logger.info("Now running Qc script on: " + file_path)
                log_name = str(self.Deliverable.id) + "_" + self.Deliverable.name + "_" + attribute +'.headerlog'
                log_dir = self.dir_service.data_dir_path_dict['headers']
                log_path = posixpath.join(log_dir,log_name)
                self.qc_log_path = log_path
                # if log exists before delete it and than redo it
                status = check_generic_path(self.DUG_connection_obj,log_path)
                script_name = self.DUG_connection_obj.DUG_project_name + "_segy-hcm"
                script_path = posixpath.join("/d/home/share/bin", script_name)
                cmd = str("nohup " + script_path + " " + file_path + " -bd " + bin_def_path + " -td " + trc_def_path + " -l " + log_path + "  > /dev/null 2>&1 &")  # change this line to modify the command and the python package needs to be changed as well
                if status == 'True':
                    message = "The log already exists either the QC is running or you are trying to run it again. Please check if the job is still running or if finished press ok to remove old file and create a new one !!"
                    self.pop_up_message_box = pop_up_message_box(message,'Warning')
                    self.pop_up_message_box.closed.connect(lambda: self.run_segy_qc(cmd,True))
                    self.pop_up_message_box.show()
                    # modify the existing Db entry
                    db_entry = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_qc_log_path == log_path).first()
                    db_entry.segy_on_disk_qc_run_status = True
                    db_entry.segy_on_disk_qc_status = None
                    db_entry.segy_on_disk_qc_approver_name = None
                    db_entry.segy_on_disk_qc_approval_time = None
                    self.db_connection_obj.sess.commit()
                else:
                    # execute the command on the DUG workstation
                    self.run_segy_qc(cmd,False)
                    db_entry = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_file_path == file_path).first()
                    db_entry.segy_on_disk_qc_run_status = True
                    db_entry.segy_on_disk_qc_log_path = log_path
                    self.db_connection_obj.sess.commit()

    def segy_qc_from_form(self,attribute):
        (bin_def_path, trc_def_path) = self.create_def_files_and_sFTP()
        file_path = posixpath.join(self.dir_service.data_dir_path_dict['data'], attribute)
        logger.info("Now running Qc script on: " + file_path)
        log_name = str(self.Deliverable.id) + "_" + self.Deliverable.name + "_" + attribute + '.headerlog'
        log_dir = self.dir_service.data_dir_path_dict['headers']
        log_path = posixpath.join(log_dir, log_name)
        self.qc_log_path = log_path
        # if log exists before delete it and than redo it
        status = check_generic_path(self.DUG_connection_obj, log_path)
        script_name = self.DUG_connection_obj.DUG_project_name + "_segy-hcm"
        script_path = posixpath.join("/d/home/share/bin", script_name)
        cmd = str(
            "nohup " + script_path + " " + file_path + " -bd " + bin_def_path + " -td " + trc_def_path + " -l " + log_path + "  > /dev/null 2>&1 &")  # change this line to modify the command and the python package needs to be changed as well
        if status == 'True':
            message = "The log already exists either the QC is running or you are trying to run it again. Please check if the job is still running or if finished press ok to remove old file and create a new one !!"
            self.pop_up_message_box = pop_up_message_box(message, 'Warning')
            self.pop_up_message_box.closed.connect(lambda: self.run_segy_qc(cmd, True))
            self.pop_up_message_box.show()
            # modify the existing Db entry
            db_entry = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
                self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_qc_log_path == log_path).first()
            db_entry.segy_on_disk_qc_run_status = True
            db_entry.segy_on_disk_qc_status = None
            db_entry.segy_on_disk_qc_approver_name = None
            db_entry.segy_on_disk_qc_approval_time = None
            self.db_connection_obj.sess.commit()
        else:
            # execute the command on the DUG workstation
            self.run_segy_qc(cmd, False)
            db_entry = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
                self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_file_path == file_path).first()
            db_entry.segy_on_disk_qc_run_status = True
            db_entry.segy_on_disk_qc_log_path = log_path
            self.db_connection_obj.sess.commit()


    def run_segy_qc(self,cmd,old_delete):
        if use_mode == 'Demo':
            logger.info("Running in Demo mode commandS will only be printed and not executed ... ")
            logger.info(str('rm -rf ' + self.qc_log_path))
            logger.info(cmd)
        elif use_mode == 'Production':
            if old_delete: # delete the old log if there
                del_cmd = str('rm -rf ' + self.qc_log_path)
                logger.info("Now deleting the old log file..")
                self.DUG_connection_obj.ws_client.exec_command(del_cmd)
                logger.info("Done...")
                logger.info("Now running the QC again")
                logger.info(cmd)
            register_entry_to_append = [cmd, 'na', self.qc_log_path, 'segy_qc',]
            append_register_entry(self.DUG_connection_obj,register_entry_to_append)

    def choose_sgy_file_for_QC(self,option):
        dir_path = self.dir_service.data_dir_path_dict['data']
        cmd = str("ls " + dir_path)
        file_list = fetch_directory_content_list(self.DUG_connection_obj,cmd)
        file_path_dict = {}
        for file_name in file_list:
            file_path_dict.update({posixpath.join(dir_path,file_name): file_name})
        file_list_show = [] # if the SEGY export status is marked as true than only QC otherwise not
        db_result = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).all()
        db_result_dict = {} # This will be used to compare
        for item in db_result:
            if item.segy_disk_export_status:
                if item.segy_on_disk_file_path in file_path_dict.keys():
                    file_list_show.append(file_path_dict[item.segy_on_disk_file_path])
        self.pop_up_combo_box = pop_up_combo_box(self, "Select File", file_list_show, 'file_sgy', option)


    def create_sgyt(self):
        self.choose_deliverable('SGYT')

    def perform_single_SEGY_QC(self):
        self.segy_qc_form = SEGY_QC_Form(self)
        self.segy_qc_form.setMinimumHeight(80)
        self.segy_qc_form.setMinimumWidth(200)
        self.segy_qc_form.show()
        #self.choose_deliverable('per_QC')

    def create_def_files_and_sFTP(self):
        # 1. create the files in the temp dir
        working_dir = os.path.join(os.getcwd(),'temp')
        file_name_bin_def = str(self.Deliverable.id) + "_" + self.Deliverable.name+"_bin.def"
        file_name_trc_def = str(self.Deliverable.id) + "_" + self.Deliverable.name+"_trc.def"
        bin_def_text = self.Deliverable.bin_def.decode('base64')
        trc_def_text = self.Deliverable.trc_def.decode('base64')
        path_bin_def = os.path.join(working_dir,file_name_bin_def)
        # check and remove if the file already exists in the temp dir
        try:
            os.remove(path_bin_def)
            logger.info("Found : " + path_bin_def)
            logger.warning("The existing file in the temp dir is now deleted, creating a new one with the same name ")
        except:
            pass
        path_trc_def = os.path.join(working_dir, file_name_trc_def)
        # check and remove if the file already exists in the temp dir
        try:
            os.remove(path_trc_def)
            logger.info("Found : " + path_trc_def)
            logger.warning("The existing file in the temp dir is now deleted, creating a new one with the same name ")
        except:
            pass
        fout_bin_def = open(path_bin_def,'wb')
        for line in bin_def_text.split('\n'):
            print >> fout_bin_def,line
        fout_bin_def.close()
        fout_trc_def = open(path_trc_def,'wb')
        for line in trc_def_text.split('\n'):
            print >> fout_trc_def, line
        fout_trc_def.close()
        # 2 now SFTP the files to the remote dir
        remote_dir = self.dir_service.data_dir_path_dict['masters']
        remote_path_bin_def = posixpath.join(remote_dir,file_name_bin_def)
        remote_path_trc_def = posixpath.join(remote_dir,file_name_trc_def)
        logger.info("Now transferring the files from the database to the DUG WS ..")
        SFTP_generic_file(self.DUG_connection_obj,path_bin_def,remote_path_bin_def)
        SFTP_generic_file(self.DUG_connection_obj,path_trc_def,remote_path_trc_def)
        logger.info("Done .. ")
        return (remote_path_bin_def,remote_path_trc_def)

    def create_sequence_wise_sgyt(self):
        result = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.Deliverable.id).filter(self.db_connection_obj.SEGY_QC_on_disk.line_name == self.sequence.real_line_name).first()
        if result is None:
            sgy_file_name = create_sgyt(self.Deliverable, self.sequence, self.IL_range, self.XL_range, int(self.reel))
            user_file_name = "user_" + sgy_file_name
            # SFTP the template to the DUG workstation
            # 1. check if the file already exists on the DUG workstation
            self.dir_service.set_deliverable(self.Deliverable)
            dir_for_checking = self.dir_service.data_dir_path_dict['masters']
            local_path = os.path.join(os.getcwd(), 'temp', sgy_file_name)
            remote_path = posixpath.join(dir_for_checking, sgy_file_name)
            status = check_generic_path(self.DUG_connection_obj, remote_path)
            logger.info("Now attempting to transfer the file to the DUG workstation...")
            if status == 'True':
                action = get_item_through_dialogue(self.parent, 'Now attempting to transfer the file to the DUG workstation... type y to continue, n to exit')
                if action == 'y':
                    SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
                else:
                    logger.warning('Aborting the file transfer!!!!')
            else:
                SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
            # now create a new DAO object
            new_obj = self.db_connection_obj.SEGY_QC_on_disk()
            new_obj.line_name = self.sequence.real_line_name
            new_obj.deliverable_id = self.Deliverable.id
            new_obj.sgyt_status = True
            new_obj.sgyt_reel_no = self.Deliverable.reel_prefix+str(self.reel)
            new_obj.sgyt_min_il = self.IL_range[0]
            new_obj.sgyt_max_il = self.IL_range[1]
            new_obj.sgyt_min_xl = self.XL_range[0]
            new_obj.sgyt_max_xl = self.XL_range[1]
            new_obj.sgyt_fgsp = self.sequence.fgsp
            new_obj.sgyt_lgsp = self.sequence.lgsp
            new_obj.sgyt_min_ffid = self.sequence.fg_ffid
            new_obj.sgyt_max_ffid = self.sequence.lg_ffid
            new_obj.sgyt_user_path = posixpath.join(dir_for_checking, user_file_name)
            new_obj.sgyt_unix_path = remote_path
            new_obj.sgyt_exp_uname = self.username
            new_obj.sgyt_time_stamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            self.db_connection_obj.sess.add(new_obj)
            self.db_connection_obj.sess.commit()
            logger.info("The new object for SEGY on disk QC SEGY template export is now added to the database...")
        else:
            message = str("The SGYT file for deliverable_id : " + str(self.Deliverable.id) + ": name : " + self.Deliverable.name + ' line name: ' + self.sequence.real_line_name + " was exported by : " + result.sgyt_exp_uname + ' on : ' + result.sgyt_time_stamp + " Enter reason to reexport: ")
            perform = change_log_creation(gui = self.parent, conn_obj=self.db_connection_obj,message = message, type_entry = "change",location = 'sgyt')
            if perform:
                sgy_file_name = create_sgyt(self.Deliverable, self.sequence, self.IL_range, self.XL_range, self.reel)
                user_file_name = "user_" + sgy_file_name
                # SFTP the template to the DUG workstation
                # 1. check if the file already exists on the DUG workstation
                self.dir_service.set_deliverable(self.Deliverable)
                dir_for_checking = self.dir_service.data_dir_path_dict['masters']
                local_path = os.path.join(os.getcwd(), 'temp', sgy_file_name)
                remote_path = posixpath.join(dir_for_checking, sgy_file_name)
                status = check_generic_path(self.DUG_connection_obj, remote_path)
                logger.info("Now attempting to transfer the file to the DUG workstation...")
                if status == 'True':
                    message = "File already exists on DUG system, type y to continue, n to exit"
                    action = get_item_through_dialogue(self.parent, message)
                    if action == 'y':
                        SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
                    else:
                        logger.warning('Aborting the file transfer!!!!')
                else:
                    SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
                # now create a new DAO object
                result.sgyt_reel_no = self.Deliverable.reel_prefix+str(self.reel)
                result.sgyt_fgsp = self.sequence.fgsp
                result.sgyt_lgsp = self.sequence.lgsp
                result.sgyt_min_ffid = self.sequence.fg_ffid
                result.sgyt_max_ffid = self.sequence.lg_ffid
                result.sgyt_min_il = self.IL_range[0]
                result.sgyt_max_il = self.IL_range[1]
                result.sgyt_min_xl = self.XL_range[0]
                result.sgyt_max_xl = self.XL_range[1]
                result.sgyt_user_path = posixpath.join(dir_for_checking, user_file_name)
                result.sgyt_unix_path = remote_path
                result.sgyt_exp_uname = self.username
                result.sgyt_time_stamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
                if result.sgyt_approval_status is not None:
                    # this step clears the previous status flag as this is a new file and should be checked again
                    result.sgyt_approval_status = None
                    result.sgyt_approver_name = None
                    result.sgyt_approval_time = None
                self.db_connection_obj.sess.commit()

    def create_SEGY_3D_sgyt(self):
        result = self.db_connection_obj.sess.query(self.db_connection_obj.SEGY_QC_on_disk).filter(
            self.db_connection_obj.SEGY_QC_on_disk.deliverable_id == self.Deliverable.id).first() # This time we do not need a sequence in the filter mocde
        if result is None:
            sgyt_file_name = create_3D_sgyt(self.Deliverable, self.IL_range, self.XL_range, int(self.reel))
            user_file_name = "user_" + sgyt_file_name
            # SFTP the template to the DUG workstation
            # 1. check if the file already exists on the DUG workstation
            self.dir_service.set_deliverable(self.Deliverable)
            dir_for_checking = self.dir_service.data_dir_path_dict['masters']
            local_path = os.path.join(os.getcwd(), 'temp', sgyt_file_name)
            remote_path = posixpath.join(dir_for_checking, sgyt_file_name)
            status = check_generic_path(self.DUG_connection_obj, remote_path)
            logger.info("Now attempting to transfer the file to the DUG workstation...")
            if status == 'True':
                action = get_item_through_dialogue(self.parent, 'Now attempting to transfer the file to the DUG workstation... type y to continue, n to exit')
                if action == 'y':
                    SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
                else:
                    logger.warning('Aborting the file transfer!!!!')
            else:
                SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
            # now create a new DAO object
            new_obj = self.db_connection_obj.SEGY_QC_on_disk()
            new_obj.line_name = '3D deliverable'
            new_obj.deliverable_id = self.Deliverable.id
            new_obj.sgyt_status = True
            new_obj.sgyt_reel_no = self.Deliverable.reel_prefix + str(self.reel)
            new_obj.sgyt_min_il = self.IL_range[0]
            new_obj.sgyt_max_il = self.IL_range[1]
            new_obj.sgyt_min_xl = self.XL_range[0]
            new_obj.sgyt_max_xl = self.XL_range[1]
            new_obj.sgyt_fgsp = None
            new_obj.sgyt_lgsp = None
            new_obj.sgyt_min_ffid = None
            new_obj.sgyt_max_ffid = None
            new_obj.sgyt_user_path = posixpath.join(dir_for_checking, user_file_name)
            new_obj.sgyt_unix_path = remote_path
            new_obj.sgyt_exp_uname = self.username
            new_obj.sgyt_time_stamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            self.db_connection_obj.sess.add(new_obj)
            self.db_connection_obj.sess.commit()
            logger.info("The new object for SEGY on disk QC SEGY template export is now added to the database...")
        else:
            message = str("The SGYT file for deliverable_id : " + str(
                self.Deliverable.id) + ": name : " + self.Deliverable.name +  " was exported by : " + result.sgyt_exp_uname + ' on : ' + result.sgyt_time_stamp + " Enter reason to re-export: ")
            perform = change_log_creation(gui=self.parent, conn_obj=self.db_connection_obj, message=message,
                                          type_entry="change", location='sgyt')
            if perform:
                sgyt_file_name = create_3D_sgyt(self.Deliverable, self.IL_range, self.XL_range, self.reel)
                user_file_name = "user_" + sgyt_file_name
                # SFTP the template to the DUG workstation
                # 1. check if the file already exists on the DUG workstation
                self.dir_service.set_deliverable(self.Deliverable)
                dir_for_checking = self.dir_service.data_dir_path_dict['masters']
                local_path = os.path.join(os.getcwd(), 'temp', sgyt_file_name)
                remote_path = posixpath.join(dir_for_checking, sgyt_file_name)
                status = check_generic_path(self.DUG_connection_obj, remote_path)
                logger.info("Now attempting to transfer the file to the DUG workstation...")
                if status == 'True':
                    message = "File already exists on DUG system, type y to continue, n to exit"
                    action = get_item_through_dialogue(self.parent, message)
                    if action == 'y':
                        SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
                    else:
                        logger.warning('Aborting the file transfer!!!!')
                else:
                    SFTP_generic_file(self.DUG_connection_obj, local_path, remote_path)
                    print "File transfer complete .. "
                # now create a new DAO object
                result.sgyt_reel_no = self.Deliverable.reel_prefix + str(self.reel)
                result.sgyt_fgsp =  None
                result.sgyt_lgsp = None
                result.sgyt_min_ffid = None
                result.sgyt_max_ffid = None
                result.sgyt_min_il = self.IL_range[0]
                result.sgyt_max_il = self.IL_range[1]
                result.sgyt_min_xl = self.XL_range[0]
                result.sgyt_max_xl = self.XL_range[1]
                result.sgyt_user_path = posixpath.join(dir_for_checking, user_file_name)
                result.sgyt_unix_path = remote_path
                result.sgyt_exp_uname = self.username
                result.sgyt_time_stamp = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
                if result.sgyt_approval_status is not None:
                    # this step clears the previous status flag as this is a new file and should be checked again
                    result.sgyt_approval_status = None
                    result.sgyt_approver_name = None
                    result.sgyt_approval_time = None
                self.db_connection_obj.sess.commit()



if __name__ == '__main__':
    test = SEGY_service()

