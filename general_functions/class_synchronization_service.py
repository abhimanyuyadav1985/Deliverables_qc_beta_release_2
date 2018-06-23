"""

This Module contains the class Synchronization_Service which is the main sync service between the Db and DUG systems

"""


from database_engine.DB_ops import check_and_add_raw_seq_info,get_deliverables_dao_objects
from database_engine.DB_ops import get_list_of_segd_deliverables
from database_engine.DB_ops import get_all_available_segd_tapes_in_orca
from database_engine.DB_ops import check_previous_passed_for_SEGD_qc
from database_engine.DB_ops import check_previous_run_for_SEGD_qc
from database_engine.DB_ops import fetch_seq_id_from_name
from database_engine.DB_ops import add_SEGD_QC_obj
from database_engine.DB_ops import check_and_add_media_list_obj
from dug_ops.DUG_ops import fetch_directory_content_list, get_SEGD_QC_status, get_SEGD_QC_run_finish_status
from Tape_services.class_tape_operation_manager import deliverable_dir_service
from Tape_services.class_tape_operation_manager import deliverable_file_service
from dug_ops.DUG_ops import return_encoded_log
from configuration.SEGY_header_type_wise import file_size_identifier

import posixpath
import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class Synchronization_service(object):
    """
    Synchronization service is the service class used to synchronize information between the DUG system and IRDB

    """

    def __init__(self,parent):
        """
        Inherit the following from the main window which is the parent for the service

        *db_connection_obj
        *DUG_connection_obj


        Create the following services for self

        *self.dir_service from the class deliverable_dir_service
        *self.file_service from the class deliverable_file_service

        """

        self.parent = parent

        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.dir_service = deliverable_dir_service(self)
        self.file_service = deliverable_file_service(self)

    def sync_all(self):

        """
        *sync raw_seq_info table in IRDB => deliverables_qc.raw_seq_info with view orca.good_sp
        *lookup IRDB to find all directory paths for various deliverables and check the DUG system to ensure they are present
        *sync media list => add all the SEGD QC verified tapes to media list ( SEGY needs to be done)
        *Auto refresh the SEGD QC status ( parse the logs that were in running status to check if the jobs are still running and if finished check the logs
        *sync SEGY file size : simply to make the current version back compatible when we were not checking the file size to store in IRDB

        """
        logger.info("Now doing statup diagnostic ... ")

        self.check_all_deliverable_dir_and_db_entries()
        self.SEGD_QC_sync()
        self.sync_segy_file_size()

        self.sync_media_list()
        logger.info("Startup diagnostic now complete ")

    def sync_segy_file_size(self):
        """
        This is only necessary because I did not put the extraction of file size in the orignal release
        search the database for all the elements in the segy_on_disk qc where segy_on_disk_qc_status is True and segy file size in Null

        """
        result = self.db_connection_obj.sess.query(
            self.db_connection_obj.SEGY_QC_on_disk
        ).filter(self.db_connection_obj.SEGY_QC_on_disk.segy_on_disk_qc_status == True).filter(
            self.db_connection_obj.SEGY_QC_on_disk.file_size == None).all()
        # Now for each element parse the log and fill file size
        if len(result) == 0:
            logger.info(" All file size in segy on disk table already present")
        else:
            for a_item in result:
                logger.info("Now updating file size for: deliverable_id: " + str(a_item.deliverable_id) + " linename: " + a_item.line_name)
                encoded_data = return_encoded_log(self.DUG_connection_obj,a_item.segy_on_disk_qc_log_path)
                log_data = encoded_data.decode('base64')
                for line in log_data.split('\n'):
                    if file_size_identifier in line.rstrip("\n"):
                        line_to_use = line.rstrip("\n")
                        line_list = line_to_use.split()
                        a_item.file_size = line_list[len(line_list) - 2]
            self.db_connection_obj.sess.commit()
            logger.info("file size update complete ..")



    def sync_raw_seq_info(self):
        """
        Uses a function check_and_add_raw_seq_info in the module database_engine.DB_ops to sync
        IRDB : deliverables_qc.raw_seq_info with orca.good_sp view

        """
        check_and_add_raw_seq_info(self.db_connection_obj)

    def get_existing_deliverables(self):
        """
        Uses a function get_deliverarables_dao_objects from database_engine.DB_ops to extract all deliverables DAO objects from IRDB

        """
        self.existing_deliverables = get_deliverables_dao_objects(self.db_connection_obj)


    def check_all_deliverable_dir_and_db_entries(self):
        """
        Check if all dir paths in the IRDB still exist on the DUG system

        """
        self.get_existing_deliverables()
        for deliverable in self.existing_deliverables:
            self.set_deliverable_for_dir_service(deliverable)
            self.dir_service.create_all_paths()
            self.dir_service.add_all_paths_to_db()

    def set_deliverable_for_dir_service(self,deliverable):
        """
        Set self.dir_service to point to a certain deliverable DAO from IRDB

        :param deliverable:

        """
        self.dir_service.set_deliverable(deliverable)

    def sync_media_list(self):
        """
        Sync SEGD and SEGY media list for media where write is QC passed

        """
        self.sync_segd_media_list()

    def sync_segd_media_list(self):
        """
        get the list of deliverables belonging to SEGD class

        get the list of available tapes from orca table, this comes from the Dao for orca.tape which has the complete list of SEGS tapes including the NTBP sequences

        uses a function check_and_add_media_entry from the module database_engine.DB_ops to add SEGS tape to media list if QC is approved
        """
        segd_deliverables_list = get_list_of_segd_deliverables(self.db_connection_obj)
        SEGD_tape_obj_list = get_all_available_segd_tapes_in_orca(self.db_connection_obj)
        for deliverable in segd_deliverables_list:
            for set in range(1,int(deliverable.copies) + 1):
                for tape in SEGD_tape_obj_list:
                    media_entry = self.db_connection_obj.Media_list()
                    media_entry.deliverable_id = deliverable.id
                    media_entry.set_no = set
                    media_entry.media_label = tape.name
                    media_entry.reel_no = tape.name
                    check_and_add_media_list_obj(self.db_connection_obj,media_entry)

    def SEGD_QC_sync(self):
        """
        Parse the logs and provide SEGD QC status from DUG system to IRDB

        """
        logger.info("Now executing SEGD QC sync...")
        #1. get the list of deliverables belonging to SEGD class
        segd_deliverables_list = get_list_of_segd_deliverables(self.db_connection_obj)
        #2. get the list of available tapes from orca table
        SEGD_tape_obj_list = get_all_available_segd_tapes_in_orca(self.db_connection_obj)
        orca_tape_name_list = []
        for orca_tape in SEGD_tape_obj_list:
            orca_tape_name_list.append(orca_tape.name)
        #3. looping over all the SEGD deliverables
        for deliverable in segd_deliverables_list:
            self.dir_service.set_deliverable(deliverable)
            for set_no in self.dir_service.qc_dir_path_dict.keys():
                qc_path_list = []
                available_path_dict = self.dir_service.qc_dir_path_dict[set_no]
                qc_path_list.append(available_path_dict['logfile'])
                for path in qc_path_list:
                    cmd = ("ls " + path)
                    available_files_list = fetch_directory_content_list(self.DUG_connection_obj,cmd)
                    tape_log_run_dict = {}
                    for file_name in available_files_list:
                        tape_label = file_name.split("--")[0]
                        dict_item =  posixpath.join(path,file_name)
                        dict_entry = {tape_label:dict_item}
                        tape_log_run_dict.update(dict_entry)
                    # check previous state
                    run_tape_obj_list =  check_previous_run_for_SEGD_qc(self.db_connection_obj,deliverable.id,set_no)
                    run_tape_list_id_set = []
                    for tape in run_tape_obj_list:
                        if tape not in run_tape_list_id_set:
                            run_tape_list_id_set.append(tape.tape_no)
                    # check previous passed state
                    passed_tape_obj_list = check_previous_passed_for_SEGD_qc(self.db_connection_obj,deliverable.id,set_no)
                    passed_tape_list_for_id_set = []
                    for tape in passed_tape_obj_list:
                        if tape not in  passed_tape_list_for_id_set:
                            passed_tape_list_for_id_set.append(tape.tape_no)
                    # Now sync old and new extries as needed
                    for orca_tape in orca_tape_name_list:
                        if orca_tape in passed_tape_list_for_id_set:
                            pass  # do nothing if the tape has already passed QC check
                        else:
                            if orca_tape in tape_log_run_dict.keys(): # check if the log exists 1st no point going ahead if the log does not exist for the tape, maybe the SEGD QC was not run yet
                                # check if a previous db entry exists
                                SEGD_qc = self.db_connection_obj.sess.query(self.db_connection_obj.SEGD_qc).filter(self.db_connection_obj.SEGD_qc.log_path == tape_log_run_dict[orca_tape]).first()
                                if SEGD_qc is None: # if no DB  entry was found for this logpath follow this step
                                    log_path = tape_log_run_dict[orca_tape] # set the log path to the log path to the tape
                                    qc_log = self.file_service.return_encoded_string(log_path) # get the QC log for the path
                                    #Add the new fields necessary for report creation
                                    x = qc_log.decode('base64')
                                    files_list = []
                                    for line in x.split('\n'):
                                        if 'Tape QC successful:' in line:
                                            files_list = (line.split(': ')[1]).split(' ')
                                        if "First FFID   :" in line:
                                            f_ffid_list = (line.split(': ')[1]).split(' ')
                                        elif 'Last  FFID' in line:
                                            l_ffid_list = (line.split(': ')[1]).split(' ')
                                        elif "Files QC'd" in line:
                                                number_files_list = (line.split(': ')[1]).split(' ')
                                        elif "Total time:" in line:
                                            date_str = ""
                                            for item in line.split("  ")[0].split(" ")[1:6]:
                                                if item == "UTC":
                                                    pass
                                                elif ":" in item:
                                                    item_a = item.split(":")
                                                    item = item_a[0] + ":" + item_a[1]
                                                    date_str = date_str + " " + str(item)
                                                else:
                                                    date_str = date_str + " " + str(item)
                                    for i in range(0,len(files_list)):
                                        #print i
                                        SEGD_qc = self.db_connection_obj.SEGD_qc()
                                        SEGD_qc.tape_no = orca_tape
                                        file_path = files_list[i].rstrip()
                                        #print file_path.split('/')[-1]
                                        SEGD_qc.line_name = file_path.split('/')[-1]
                                        SEGD_qc.seq_id = fetch_seq_id_from_name(self.db_connection_obj,
                                                                                SEGD_qc.line_name)
                                        SEGD_qc.deliverable_id = deliverable.id
                                        SEGD_qc.set_no = set_no
                                        SEGD_qc.log_path = tape_log_run_dict[orca_tape]
                                        SEGD_qc.qc_status = get_SEGD_QC_status(self.DUG_connection_obj,
                                                                               SEGD_qc.log_path)
                                        SEGD_qc.run_status = True
                                        SEGD_qc.label_test = True
                                        SEGD_qc.use_status = True
                                        SEGD_qc.run_finish = True
                                        SEGD_qc.date_time_str = date_str
                                        SEGD_qc.f_ffid = f_ffid_list[i]
                                        SEGD_qc.l_ffid = l_ffid_list[i]
                                        SEGD_qc.missing = 0
                                        SEGD_qc.number_files = number_files_list[i]
                                        add_SEGD_QC_obj(self.db_connection_obj,SEGD_qc)
                                        self.db_connection_obj.sess.commit()
                                else: # looks like this log path appears in the list, this means the sync service has gone through this before
                                    SEGD_qc_list = self.db_connection_obj.sess.query(self.db_connection_obj.SEGD_qc).filter(
                                        self.db_connection_obj.SEGD_qc.log_path == tape_log_run_dict[orca_tape]).all()
                                    for SEGD_qc in SEGD_qc_list:
                                        log_path = tape_log_run_dict[orca_tape]  # set the log path to the log path to the tape
                                        qc_log = self.file_service.return_encoded_string(log_path)  # get the QC log for the path
                                        # Add the new fields necessary for report creation
                                        x = qc_log.decode('base64')
                                        files_list = []
                                        for line in x.split('\n'):
                                            if 'Tape QC successful:' in line:
                                                files_list = (line.split(': ')[1]).split(' ')
                                            if "First FFID   :" in line:
                                                f_ffid_list = (line.split(': ')[1]).split(' ')
                                            elif 'Last  FFID' in line:
                                                l_ffid_list = (line.split(': ')[1]).split(' ')
                                            elif "Files QC'd" in line:
                                                number_files_list = (line.split(': ')[1]).split(' ')
                                            elif "Total time:" in line:
                                                date_str = ""
                                                for item in line.split("  ")[0].split(" ")[1:6]:
                                                    if item == "UTC":
                                                        pass
                                                    elif ":" in item:
                                                        item_a = item.split(":")
                                                        item = item_a[0] + ":" + item_a[1]
                                                        date_str = date_str + " " + str(item)
                                                    else:
                                                        date_str = date_str + " " + str(item)
                                        # create a dict for sequence and other things associated with it
                                        dict_to_update = {}
                                        for i in range(0,len(files_list)):
                                            file_path = files_list[i].rstrip()
                                            # print file_path.split('/')[-1]
                                            line_name = file_path.split('/')[-1]
                                            dict_to_update.update({line_name:[f_ffid_list[i], l_ffid_list[i], number_files_list[i]]})
                                        #Now update the object
                                        SEGD_qc.qc_status = get_SEGD_QC_status(self.DUG_connection_obj,
                                                                               SEGD_qc.log_path)
                                        SEGD_qc.run_finish = True
                                        SEGD_qc.run_status = True
                                        SEGD_qc.label_test = True
                                        SEGD_qc.use_status = True
                                        SEGD_qc.date_time_str = date_str
                                        SEGD_qc.f_ffid = dict_to_update[SEGD_qc.line_name][0]
                                        SEGD_qc.l_ffid = dict_to_update[SEGD_qc.line_name][1]
                                        SEGD_qc.missing = 0
                                        SEGD_qc.number_files = dict_to_update[SEGD_qc.line_name][2]
                                        self.db_connection_obj.sess.commit()
        logger.info('SEGD QC sync finished')
















