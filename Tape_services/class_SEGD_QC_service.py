from configuration import *
from dug_ops.DUG_ops import fetch_directory_content_list
from database_engine.DB_ops import get_list_of_applicable_SEGD_tapes,get_min_max_ffid_tuple_for_tape, get_all_segd_objects_for_set_checked_before
import posixpath
from dug_ops.DUG_ops import append_register_entry
from database_engine.DB_ops import get_all_raw_seq_info_objects
from configuration import get_segd_qc_script
from database_engine.DB_ops import get_segd_qc_path

import logging
from app_log import  stream_formatter

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)



class SEGD_QC_service(object):
    def __init__(self,parent):
        self.parent = parent
        self.name = "SEGD_QC_service"
        self.segd_qc_script = get_segd_qc_script()
        logger.info("SEGD QC Script: " + self.segd_qc_script)

    def setup_execution(self,reel_no,file_list,deliverable,drive,set, split_line):
        self.reel_no = reel_no
        self.deliverable = deliverable
        self.dst = drive
        self.file_list = file_list
        self.set = set
        self.split_line = split_line
        self.set_SEGD_path()
        self.set_logfile()
        self.run()


    def run(self):
        if self.split_line == True:
            run_cmd = str("nohup " + self.segd_qc_script + " tape=/dev/" + str(self.dst)+ " disk=" + self.SEGD_path_string + " log=" + str(self.logfile) + " firstdisk=" + str(self.min_ffid) + " lastdisk=" + str(self.max_ffid) + ' > /dev/null 2>&1 &')
        else:
            run_cmd = str("nohup " + self.segd_qc_script + " tape=/dev/" + str(self.dst) + " disk=" +
                self.SEGD_path_string + " log=" + str(self.logfile) + ' > /dev/null 2>&1 &')
        if use_mode == 'Demo':
            logger.warning("Running in DEMO mode command will only be printed not executed ....")
        elif use_mode == 'Production':
            logger.info("Now sending to DUG buffer: " + run_cmd)
            self.check_for_previous_run()
            segd_qc_register_obj = [run_cmd , self.dst, self.logfile , 'segd_qc']
            append_register_entry(self.parent.DUG_connection_obj,segd_qc_register_obj)

    def check_for_previous_run(self):
        result = self.parent.db_connection_obj.sess.query(self.parent.db_connection_obj.SEGD_qc).filter(
            self.parent.db_connection_obj.SEGD_qc.log_path == self.logfile).first()
        if result == None:
            pass
        else:
            logger.warning("Previous run deltected .. deleting it from database for integrity..")
            self.parent.db_connection_obj.sess.delete(result)
            self.parent.db_connection_obj.sess.commit()


    def set_SEGD_path(self):
        self.SEGD_path_string = ''
        for i in range(0,len(self.file_list)):
            self.SEGD_path_string = self.SEGD_path_string + ' ' + posixpath.join(self.parent.dir_service.data_dir_path_dict['segd.segd'],self.file_list[i])
        logger.info("The SEGD data directory set")

    def set_logfile(self):
        search_obj = get_segd_qc_path(self.parent.db_connection_obj, self.parent.deliverable.id, self.set)
        dir_path = search_obj.path
        file_name = self.reel_no + "--set" + self.parent.set_no + '.log'
        self.logfile= posixpath.join(dir_path, file_name)
        logger.info("The log file set :: " + self.logfile)

    def get_list_of_available_segd_seq(self):
        dir_path = self.parent.dir_service.data_dir_path_dict['segd.segd']
        cmd = str("ls " + dir_path)
        dir_list_for_combo = fetch_directory_content_list(self.parent.DUG_connection_obj,cmd)
        return dir_list_for_combo

    def get_list_of_unchecked_SEGD_seq_for_set(self,all_seq_list):
        raw_seq_info_dao_list = get_all_raw_seq_info_objects(self.parent.db_connection_obj)
        seq_line_dict = {}
        for a_dao in raw_seq_info_dao_list:
            seq_line_dict.update({a_dao.seq : a_dao.real_line_name})
        previous_check_line_list = []
        previous_checked_list = get_all_segd_objects_for_set_checked_before(self.parent.db_connection_obj, self.parent.deliverable.id, self.parent.set_no)
        for a_dao in previous_checked_list:
            previous_check_line_list.append(seq_line_dict[a_dao.seq_id])
        return_list = []
        for a_line in all_seq_list:
            if a_line in previous_check_line_list:
                pass
            else:
                return_list.append(a_line)

        return return_list


    def get_list_of_applicable_segd_tapes(self, file_list):
        tape_list = get_list_of_applicable_SEGD_tapes(self.parent.db_connection_obj,file_list)
        return tape_list

    def set_min_max_ffid(self):
        (self.min_ffid,self.max_ffid) = get_min_max_ffid_tuple_for_tape(self.parent.db_connection_obj,self.parent.reel_no)

if __name__ == '__main__':
    test = SEGD_QC_service()

