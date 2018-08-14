import psycopg2
# -*- coding: utf-8 -*-
import pickle
from configuration import *
from unipath import Path
import sys
from sqlalchemy import or_,and_
import time

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

from functools import wraps

def logger_util(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        ts = time.time()
        result = func(*args,**kwargs)
        te = time.time()
        time_string = "{:8.5f} sec".format(te-ts)
        logger.info("Finished executing: " + func.__name__ + "  <Execution time => " + time_string)
        return result
    return with_logging


#------------------------------------------------------------------------------------------------------------
#Function to check the connection to the desired database_engine in from configuration setup
#------------------------------------------------------------------------------------------------------------
@logger_util
def test_DB_connection(curr):
    logger.info("Testing the DB connection now ......")
    try:
        curr.execute("SELECT VERSION()")
        results = curr.fetchone()
        ver = results[0]
        if (ver is None):
            logger.warning("Please check the details once again as we cannot find Postgres vversion ")
            return False
        else:
            logger.info("Postgres version: " + ver)
            return
    except Exception as error:
        logger.error(error)
        return False

@logger_util
def test_db_connection_for_config(obj):
    db_name = str(obj.db_name.text())
    db_user = str(obj.db_user.text())
    db_pword = str(obj.db_pword.text())
    db_port = str(obj.db_port.text())

    host_IP = str(obj.host_IP.text())
    host_user = str(obj.host_user.text())
    host_pword = str(obj.host_pword.text())
    try:
        conn = psycopg2.connect(database=db_name, user=db_user, password=db_pword, port=1111)
        curr = conn.cursor()
        test_DB_connection(curr)
        curr.close()
        logger.info("Connection to database_engine successful !!!!!!!!!!!!!!!")
    except Exception as error:
        logger.error("Unable to connect to the Server, Does the tunnel from database server to local port 1111 exist ????")
        logger.error(error)
        logger.error("Exiting application now")
        sys.exit()

@logger_util
def fetch_config_info():
    file_path = os.path.join(os.getcwd(), conn_config_file)
    logger.info("config_file: " + file_path)
    file_handler = open(file_path, "rb")
    obj_config = pickle.load(file_handler)
    file_handler.close()
    db_name = str(obj_config.db_name)
    db_user = str(obj_config.db_user)
    host_IP = str(obj_config.host_IP)
    DUG_host = obj_config.DUG_IP
    DUG_user = obj_config.DUG_user
    dug_path = obj_config.DUG_segy_path
    return [host_IP, db_user, db_name, DUG_host, DUG_user, dug_path]

#-----------------------------------------------------------------------------------------------------------
# Get the project information dictionary
#-----------------------------------------------------------------------------------------------------------
@logger_util
def fetch_project_info(obj):
    search_result = obj.sess.query(obj.Project_info).order_by(obj.Project_info.ip).all()
    return search_result


#-------------------------------------------------------------------------------------------------------------
# Deliverables functions
#--------------------------------------------------------------------------------------------------------------
@logger_util
def fetch_deliverables_list(obj):
    search_result  = obj.sess.query(obj.Deliverables).order_by(obj.Deliverables.id).all()
    search_list = []
    for deliliverable_item in search_result:
        search_list.append(deliliverable_item.__dict__)
    return search_list

@logger_util
def fetch_shipments_list(obj):
    search_result = obj.sess.query(obj.Shipments).order_by(obj.Shipments.id).all()
    search_list = []
    for shipment_item in search_result:
        search_list.append(shipment_item.__dict__)
    return search_list

@logger_util
def add_deliverable(obj, dao_object):
    obj.sess.add(dao_object)
    obj.sess.commit()

@logger_util
def add_shipment(obj,dao_object):
    obj.sess.add(dao_object)
    obj.sess.commit()

@logger_util
def fetch_single_deliverable(obj,id):
    search_result = obj.sess.query(obj.Deliverables).filter(obj.Deliverables.id == id).all()
    return search_result[0].__dict__

@logger_util
def delete_deliverable_obj(obj,id):
    deliverable_to_delete = obj.sess.query(obj.Deliverables).filter(obj.Deliverables.id == id)
    deliverable_to_delete.delete()
    obj.sess.commit()

@logger_util
def delete_shipment_obj(obj,id):
    shipment_to_delete = obj.sess.query(obj.Shipments).filter(obj.Shipments.id == id)
    shipment_to_delete.delete()
    obj.sess.commit()

@logger_util
def add_deliverable_data_dir(obj,dao_object):
    if obj.sess.query(obj.Deliverables_data_dir).filter(obj.Deliverables_data_dir.path == dao_object.path).count() >0:
        logger.warning(dao_object.path + "  exists in database ..")
        return False
    else:
        logger.info("Now adding to Db::" + dao_object.path)
        obj.sess.add(dao_object)
        obj.sess.commit()
        return False

@logger_util
def add_deliverable_qc_dir(obj,dao_object):
    if obj.sess.query(obj.Deliverables_qc_dir).filter(obj.Deliverables_qc_dir.path == dao_object.path).count() > 0:
        logger.warning(dao_object.path + "  exists in database ..")
        return False
    else:
        logger.info("Now adding to db:: " + dao_object.path)
        obj.sess.add(dao_object)
        obj.sess.commit()
        return False

@logger_util
def verify_if_deliverable_id_is_correct(obj,id):
    deliverable_list = obj.sess.query(obj.Deliverables).order_by(obj.Deliverables.id).all()
    id_list = []
    for deliverable in deliverable_list:
        id_list.append(str(deliverable.id))
    if id in id_list:
        return True
    else:
        return False

@logger_util
def get_deliverable_object(obj,id):
    deliverable =  obj.sess.query(obj.Deliverables).filter(obj.Deliverables.id == id).first()
    return deliverable

@logger_util
def check_and_add_raw_seq_info(obj):
    cmd = """
        SELECT l.sequence_number AS seq,
            l.real_line_name,
            l.preplot_name,
            a.first_ffid,
            a.first_shot,
            orca.ffid(l.sequence_number, e.fgsp) AS fg_ffid,
            e.fgsp,
            orca.ffid(l.sequence_number, e.lgsp) AS lg_ffid,
            e.lgsp,
            a.last_ffid,
            a.last_shot,
            to_char(l.start_time, 'DD-MM-YYYY'::text) AS start_data
           FROM orca.line l
             JOIN orca.edit_good_shot_point e USING (sequence_number)
             JOIN orca.all_sp a USING (sequence_number)
          ORDER BY l.sequence_number;
          """
    s = obj.scoped_session()
    result = s.execute(cmd)
    s.close()
    logger.info("Now synchronizing the Raw seq info for orca data ")

    for seq_data in result:
        new_entry = obj.Raw_seq_info()
        (new_entry.seq, new_entry.real_line_name, new_entry.preplot_name, new_entry.first_ffid, new_entry.first_shot,new_entry.fg_ffid, new_entry.fgsp, new_entry.lg_ffid, new_entry.lgsp, new_entry.last_ffid, new_entry.last_shot,new_entry.start_data) = seq_data
        old_object = obj.sess.query(obj.Raw_seq_info).filter(obj.Raw_seq_info.seq == new_entry.seq).first()
        if old_object != None:
            for a_key in new_entry.__dict__.keys():
                if a_key == '_sa_instance_state':
                    pass
                else:
                    if str(new_entry.__dict__[a_key]) == str(old_object.__dict__[a_key]):
                        pass
                    else:
                        logger.info("Update => " +str(new_entry.seq) + " : " + str(a_key) + " old: " + str(
                            old_object.__dict__[a_key]) + " new: " + str(new_entry.__dict__[a_key]))
                        if new_entry.__dict__[a_key] != None:
                            setattr(old_object, a_key, str(new_entry.__dict__[a_key]))

                        else:
                            logger.info("Omit as the new entry is None")

        else:
               logger.info("creating the new entry for " + str(new_entry.seq) + " ")
               obj.sess.add(new_entry)
               logger.info("done...")
    obj.sess.commit()

@logger_util
def get_deliverables_dao_objects(obj):
    search_result = obj.sess.query(obj.Deliverables).order_by(obj.Deliverables.id).all()
    return search_result

@logger_util
def get_segd_qc_path(obj,id,set_no):
    search_obj = obj.sess.query(obj.Deliverables_qc_dir).filter(obj.Deliverables_qc_dir.deliverable_id == id).filter(obj.Deliverables_qc_dir.set_number == set_no).first()
    return search_obj

@logger_util
def get_list_of_applicable_SEGD_tapes(obj, seq_name):
    tape_list = []
    for a_seq_name in seq_name:
        seq_from_raw_seq_info = obj.sess.query(obj.Raw_seq_info).filter(obj.Raw_seq_info.real_line_name == a_seq_name).first()
        seq_id = seq_from_raw_seq_info.seq
        tapes = obj.sess.query(obj.SEGD_tapes).filter(obj.SEGD_tapes.sequence_number == seq_id).all()
        for a_tape in tapes:
            if a_tape not in tape_list:
                tape_list.append(a_tape.name)
    return tape_list

@logger_util
def get_min_max_ffid_tuple_for_tape(obj,tape_name):
    entry = obj.sess.query(obj.SEGD_tapes).filter(obj.SEGD_tapes.name == tape_name).first()
    min_ffid = entry.first_ffid
    max_ffid = entry.last_ffid
    return (min_ffid,max_ffid)

@logger_util
def get_list_of_segd_deliverables(obj):
    deliverables_list = obj.sess.query(obj.Deliverables).filter(obj.Deliverables.class_d == 'SEGD').order_by(obj.Deliverables.id).all()
    return deliverables_list

@logger_util
def get_all_available_segd_tapes_in_orca(obj):
    tape_obj_list = obj.sess.query(obj.SEGD_tapes).order_by(obj.SEGD_tapes.name).all()
    return tape_obj_list

@logger_util
def check_previous_passed_for_SEGD_qc(obj,id,set_no):
    result = obj.sess.query(obj.SEGD_qc).filter(obj.SEGD_qc.qc_status == True, obj.SEGD_qc.deliverable_id == id,obj.SEGD_qc.set_no == set_no).order_by(obj.SEGD_qc.tape_no).all()
    return result

@logger_util
def check_previous_run_for_SEGD_qc(obj,id,set_no):
    result = obj.sess.query(obj.SEGD_qc).filter(obj.SEGD_qc.run_status == True, obj.SEGD_qc.deliverable_id == id,
                                                obj.SEGD_qc.set_no == set_no).order_by(obj.SEGD_qc.tape_no).all()
    return result


def fetch_seq_id_from_name(obj,seq_name):
    seq_from_raw_seq_info = obj.sess.query(obj.Raw_seq_info).filter(obj.Raw_seq_info.real_line_name == seq_name).first()
    seq_id = seq_from_raw_seq_info.seq
    return seq_id

@logger_util
def add_SEGD_QC_obj(obj,dao_obj):
    logger.info("Now adding to SEGD QC DB Table: " + str(dao_obj.deliverable_id)+ " Set no: " + str(dao_obj.set_no) + " Tape no: " + dao_obj.tape_no)
    obj.sess.add(dao_obj)
    obj.sess.commit()

@logger_util
def get_all_production_sequences(obj):
    prod_seq_list = obj.sess.query(obj.Raw_seq_info).order_by(obj.Raw_seq_info.seq).all()
    return prod_seq_list


def fetch_seq_name_from_id(obj,seq_id):
    seq_from_raw_seq_info = obj.sess.query(obj.Raw_seq_info).filter(obj.Raw_seq_info.seq == seq_id).first()
    if seq_from_raw_seq_info is not None:
        seq_name = seq_from_raw_seq_info.real_line_name
    else:
        seq_name = "NTBP"
    return seq_name

@logger_util
def get_all_SEGD_qc_entries(obj):
    segd_qc_list = obj.sess.query(obj.SEGD_qc).order_by(obj.SEGD_qc.tape_no).all()
    return segd_qc_list

@logger_util
def get_project_name(obj):
    project_info = obj.sess.query(obj.Project_info).order_by(obj.Project_info.ip).first()
    if project_info is None:
        return None
    else:
        project_name = project_info.project
        return project_name

@logger_util
def get_list_of_SEGY_deliverables(obj):
    deliverables_list = obj.sess.query(obj.Deliverables).filter(obj.Deliverables.class_d == 'SEGY').order_by(obj.Deliverables.id).all()
    return deliverables_list

@logger_util
def get_list_of_seq_SEGY_deliverables(obj):
    deliverables_list = obj.sess.query(obj.Deliverables).filter(obj.Deliverables.class_d == 'SEGY').filter(obj.Deliverables.type == 'SEQG').order_by(obj.Deliverables.id).all()
    return deliverables_list

@logger_util
def get_SEGD_QC_object_list_for_deliverable_set(obj,deliverable_id,set_no):
    obj_list = obj.sess.query(obj.SEGD_qc).filter(obj.SEGD_qc.deliverable_id == deliverable_id ).filter(obj.SEGD_qc.set_no == set_no).order_by(obj.SEGD_qc.seq_id).all()
    return obj_list

@logger_util
def check_and_add_media_list_obj(obj,media_obj):
    status = obj.sess.query(obj.Media_list).filter(obj.Media_list.deliverable_id == media_obj.deliverable_id).filter(obj.Media_list.set_no == media_obj.set_no).filter(obj.Media_list.media_label == media_obj.media_label).first()
    if status == None:
        obj.sess.add(media_obj)
        obj.sess.commit()
    else:
        pass

@logger_util
def fetch_shipment_objects_list(obj):
    obj_list = obj.sess.query(obj.Shipments).order_by(obj.Shipments.id).all()
    return obj_list

@logger_util
def fetch_deliverable_objects_list(obj):
    obj_list = obj.sess.query(obj.Deliverables).order_by(obj.Deliverables.id).all()
    return obj_list

@logger_util
def fetch_media_list_did_set(obj,deliverable_id,set_no):
    obj_list = obj.sess.query(obj.Media_list).filter(obj.Media_list.deliverable_id ==  deliverable_id).filter(obj.Media_list.set_no == set_no).all()
    return obj_list

@logger_util
def add_usb_list_obj(obj, new_usb_label):
    obj.sess.add(new_usb_label)
    obj.sess.commit()

@logger_util
def check_usb_list_obj(obj, new_usb_name):
    result = obj.sess.query(obj.USB_list).filter(obj.USB_list.label == new_usb_name).first()
    return result

@logger_util
def fetch_usb_list_dict(obj):
    search_result = obj.sess.query(obj.USB_list).order_by(obj.USB_list.usb_id).all()
    search_list = []
    for item in search_result:
        search_list.append(item.__dict__)
    return search_list

@logger_util
def delete_usb_list_obj(obj,id):
    obj_to_delete = obj.sess.query(obj.USB_list).filter(obj.USB_list.usb_id == id)
    #print deliverable_to_delete
    obj_to_delete.delete()
    obj.sess.commit()

@logger_util
def get_all_available_usb(obj):
    result = obj.sess.query(obj.USB_list).order_by(obj.USB_list.usb_id).all()
    return result

@logger_util
def get_all_SEGY_deliverable_for_tape_write(obj):
    result = obj.sess.query(obj.Deliverables).filter(obj.Deliverables.class_d == 'SEGY').filter(or_(obj.Deliverables.media == '3592 JA', obj.Deliverables.media == '3592 JC',
                                                                                                    obj.Deliverables.media == '3592 JA multiple', obj.Deliverables.media =='3592 JC multiple')).all()
    return result


def return_SEGD_QC_log_path(obj, tape_no, set_no):
    result = obj.sess.query(obj.SEGD_qc).filter(and_(obj.SEGD_qc.tape_no == tape_no, obj.SEGD_qc.set_no == set_no)).first()
    return result.log_path

@logger_util
def return_shipment_content_from_number(obj,shipment_no):
    result = obj.sess.query(obj.Media_list).filter(obj.Media_list.shipment_no == shipment_no).order_by(obj.Media_list.box_no).order_by(obj.Media_list.reel_no).all()
    return result


@logger_util
def get_all_SEGD_QC_for_deliverable(obj,deliverable_id):
    obj_list = obj.sess.query(obj.SEGD_qc).filter(obj.SEGD_qc.deliverable_id == deliverable_id).order_by(obj.SEGD_qc.set_no).order_by(obj.SEGD_qc.tape_no).all()
    return obj_list

@logger_util
def get_all_SEGY_write_objects(obj):
    obj_list = obj.sess.query(obj.SEGY_write).all()
    return obj_list

@logger_util
def get_all_SEGY_qc_objects(obj, deliverable_id):
    obj_list = obj.sess.query(obj.SEGY_QC_on_disk).filter(obj.SEGY_QC_on_disk.deliverable_id == deliverable_id).all()
    return obj_list

@logger_util
def get_all_segd_objects_for_set_checked_before(obj,deliverable_id, set_no):
    obj_list = obj.sess.query(obj.SEGD_qc).filter(obj.SEGD_qc.deliverable_id == deliverable_id).filter(obj.SEGD_qc.set_no == set_no).filter(obj.SEGD_qc.qc_status == True).all()
    return obj_list

@logger_util
def get_all_raw_seq_info_objects(obj):
    obj_list = obj.sess.query(obj.Raw_seq_info).all()
    return obj_list

@logger_util
def get_data_for_SEGY_qc(obj, deliverable_id):
    result = obj.sess.query(obj.SEGY_QC_on_disk).filter(obj.SEGY_QC_on_disk.deliverable_id == deliverable_id).order_by(obj.SEGY_QC_on_disk.id_seq_segy_qc).all()
    return result

@logger_util
def get_seq_list_from_line_name_list(obj, line_name_list):
    result_dict = {}
    for a_line_name in line_name_list:
        try:
            raw_seq_obj = obj.sess.query(obj.Raw_seq_info).filter(obj.Raw_seq_info.real_line_name == str(a_line_name)).first()
            result_dict.update({raw_seq_obj.seq : a_line_name})
        except:
            pass
    #print result_dict
    return  result_dict

if __name__=="__main__":
    fetch_deliverables_list()
