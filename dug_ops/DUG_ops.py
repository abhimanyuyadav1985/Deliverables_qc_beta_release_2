
#imports

from configuration import *
import os
import pickle
import posixpath
import shutil
import socket
import time
import uuid

from app_log import stream_formatter

import logging
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

file_path = os.path.join(os.getcwd(), conn_config_file)

def main():
    print "You are in DUG ops script"

# def transfer_task_logger(DUG_connection_obj):
#     print "Now transferring task_logger",
#     file_path_2 = '/d/home/share/bin/task_logger.py'
#     local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'task_logger.py')
#     DUG_connection_obj.sftp_client.put(local_path_2, file_path_2)
#     print "done.."

@logger_util
def transfer_sgyt_encoder(DUG_connection_obj):
    file_path_2 = '/d/home/share/bin/strip_sgyt_and_send_encoded.py'
    local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'strip_sgyt_and_send_encoded.py')
    DUG_connection_obj.sftp_client.put(local_path_2, file_path_2)

@logger_util
def transfer_run_log_fetcher(DUG_connection_obj):
    file_path_2 = '/d/home/share/bin/run_log_fetcher.py'
    local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'run_log_fetcher.py')
    DUG_connection_obj.sftp_client.put(local_path_2, file_path_2)

@logger_util
def transfer_directory_checking_script(sftp_client):
    file_path_2 = '/d/home/share/bin/directory_checking_script.py'
    local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'directory_checking_script.py')
    sftp_client.put(local_path_2, file_path_2)


def check_generic_path(DUG_connection_obj,path_to_check):
    cmd = "python " + '/d/home/share/bin/directory_checking_script.py ' + path_to_check
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)
    outlines = stdout.readlines()
    status = outlines[0].rstrip()
    #print "The status from generic path check ==" + status
    return status

@logger_util
def transfer_SEGD_QC_parser_script(DUG_connection_obj):
    path_to_check = '/d/home/share/bin/SEGD_QC_parser.py'
    status = check_generic_path(DUG_connection_obj, path_to_check)
    logger.info(status)
    #if status == "False":
    file_path_2 = '/d/home/share/bin/SEGD_QC_parser.py'
    local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'SEGD_QC_parser.py')
    DUG_connection_obj.sftp_client.put(local_path_2, file_path_2)

@logger_util
def transfer_base_64_encoder(DUG_connection_obj):
    path_to_check = '/d/home/share/bin/base_64_encoder.py'
    status = check_generic_path(DUG_connection_obj, path_to_check)
    logger.info(status)
    #if status == "False":
    file_path_2 = '/d/home/share/bin/base_64_encoder.py'
    local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'base_64_encoder.py')
    DUG_connection_obj.sftp_client.put(local_path_2, file_path_2)

@logger_util
def transfer_SEGY_check_script(DUG_connection_obj):
    dug_path = str(DUG_connection_obj.DUG_proj_path)
    project_name = str(DUG_connection_obj.DUG_project_name)
    path_to_check = dug_path + '/segy-hdr-chk-mp.tar.gz'

    status = check_generic_path(DUG_connection_obj,path_to_check)
    logger.info(status)
    if status == "False":
        file_path_2 = dug_path + '/segy-hdr-chk-mp.tar.gz'
        local_path_2 = os.path.join(os.getcwd(), "dug_ops", 'segy-hdr-chk-mp.tar.gz')
        logger.info("Transferring the SEGY checking scripts..... ")
        DUG_connection_obj.sftp_client.put(local_path_2, file_path_2)
        logger.info("done..")
    logger.info("Checking if it has been decompressed before and softlink created..")
    path_to_check = '/d/home/share/bin/' + project_name + "_segy-hcm"
    status = check_generic_path(DUG_connection_obj,path_to_check)
    logger.info(status)
    if status == "False":
        logger.info("Now decompressing the tarball and creating the softlink..")
        decompress_and_softlink_creation(DUG_connection_obj,path_to_check)

@logger_util
def transfer_run_daemons(DUG_connection_obj):
    create_register_paths(DUG_connection_obj)
    transfer_task_execution_daemon(DUG_connection_obj)
    transfer_task_database(DUG_connection_obj)

@logger_util
def create_register_paths(DUG_connection_obj):
    dug_path = str(DUG_connection_obj.DUG_proj_path)
    path_list = [posixpath.join(dug_path,'register'),posixpath.join(dug_path,'register','from_app')]
    for a_path in path_list:
        status = check_generic_path(DUG_connection_obj,a_path)
        if status =='False':
            logger.info("Creating : " + a_path)
            create_generic_directory(DUG_connection_obj,a_path)
        else:
            logger.info('Found : ' + a_path)

@logger_util
def transfer_task_execution_daemon(DUG_connection_obj):
    dug_path = str(DUG_connection_obj.DUG_proj_path)
    path_to_check = posixpath.join(dug_path,'register','deliverables_qc_task_execution_daemon.py')
    status = check_generic_path(DUG_connection_obj, path_to_check)
    logger.info(status)
    if status == "False":
        file_path = path_to_check
        local_path = os.path.join(os.getcwd(),'dug_ops','deliverables_qc_task_execution_daemon.py')
        logger.info("Transferring the Deliverablaes QC task execution Daemon..... ")
        DUG_connection_obj.sftp_client.put(local_path, file_path)
        logger.info("done..")
    else:
        logger.info("Task execution daemaon already exits ..... ")

@logger_util
def transfer_task_database(DUG_connection_obj):
    dug_path = str(DUG_connection_obj.DUG_proj_path)
    path_to_check = posixpath.join(dug_path, 'register', 'task_database.sqlite3')
    status = check_generic_path(DUG_connection_obj, path_to_check)
    logger.info(status)
    if status == "False":
        file_path = path_to_check
        local_path = os.path.join(os.getcwd(), 'dug_ops', 'task_database.sqlite3')
        logger.info("Transferring the Blank task database.... ")
        DUG_connection_obj.sftp_client.put(local_path, file_path)
        logger.info("done..")
    else:
        logger.info("Task database already exists..... ")

@logger_util
def decompress_and_softlink_creation(DUG_connection_obj,path_to_check):
    DUG_segy_path = str(DUG_connection_obj.DUG_proj_path)
    cmd = "tar -xf " + DUG_segy_path + "/segy-hdr-chk-mp.tar.gz -C " + DUG_segy_path + "/"
    DUG_connection_obj.ws_client.exec_command(cmd)
    logger.info("decompression done..")
    cmd = "ln -s " + DUG_segy_path + '/segy-hdr-chk-mp/segy-hdr-chk-mp ' + path_to_check
    DUG_connection_obj.ws_client.exec_command(cmd)
    logger.info("softlink created ..")

@logger_util
def create_generic_directory(DUG_connection_obj,path_to_create):
    cmd = "mkdir " + path_to_create
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)
    if  stdout.readlines()==[] and stderr.readlines() == []:
        return True
    else:
        return False

@logger_util
def run_command_on_tape_server(DUG_connection_obj,cmd,dev_to_use):
    #now 1st check the busy device file
    path_dev_file = os.path.join(os.getcwd(),'temp','busy_dev')
    if os.path.exists(path_dev_file):
        file_handler = open(path_dev_file,'rb')
        busy_dev_list = pickle.load(file_handler)
        file_handler.close()
    else:
        busy_dev_list = []
    if dev_to_use in busy_dev_list:
        logger.info("Aborting Busy: " + dev_to_use)
        return None
    else:
        logger.info("Executing : " + cmd)
        stdin, stdout, stderr = DUG_connection_obj.ts_client.exec_command(cmd)
        logger.info("done .. ")
        return stdout

@logger_util
def run_command_on_ws_client(DUG_connection_obj,cmd):
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)

@logger_util
def fetch_directory_content_list(DUG_connection_obj,cmd):
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)
    directory_listing = []
    for item in stdout.readlines():
        directory_listing.append(item.rstrip())
    return directory_listing

@logger_util
def get_SEGD_QC_status(DUG_conenction_obj, path):
    cmd = str('python /d/home/share/bin/SEGD_QC_parser.py ' + path )
    stdin, stdout, stderr = DUG_conenction_obj.ws_client.exec_command(cmd)
    std_out = []
    for line in stdout.readlines():
        std_out.append(line)
    if int(std_out[0][1]) == 1:
        return True
    else:
        return False

@logger_util
def get_SEGD_QC_run_finish_status(DUG_conenction_obj, path):
    cmd = str('python /d/home/share/bin/SEGD_QC_parser.py ' + path)
    stdin, stdout, stderr = DUG_conenction_obj.ws_client.exec_command(cmd)
    std_out = []
    for line in stdout.readlines():
        std_out.append(line)
    logger.info(std_out[0])
    if int(std_out[0][0]) == 1:
        return True
    else:
        return False

@logger_util
def SFTP_generic_file(DUG_connection_obj,local_path,remote_path):
    DUG_connection_obj.sftp_client.put(local_path, remote_path)

@logger_util
def return_encoded_log(DUG_connection_obj,log_path):
    cmd = str('python /d/home/share/bin/base_64_encoder.py ' + log_path)
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)
    return stdout.read()


@logger_util
def return_encoded_stripped_sgyt(DUG_connection_obj,sgyt_path):
    cmd = str('python /d/home/share/bin/strip_sgyt_and_send_encoded.py ' + sgyt_path)
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)
    return stdout.read()


@logger_util
def get_file_timestamp(DUG_connection_obj,file_path):
    cmd = str('stat ' + file_path)
    stdin, stdout, stderr = DUG_connection_obj.ws_client.exec_command(cmd)
    std_out = []
    for line in stdout.readlines():
        std_out.append(line)
    return std_out

@logger_util
def create_a_pickle_file_for_command(register_obj):
    status = 'queue'
    sysip = str(socket.gethostbyname(socket.gethostname()))
    submit_time = time.strftime("%Y%m%d-%H%M%S")
    run_cmd = register_obj[0]
    tape_drive = register_obj[1]
    log_path = register_obj[2]
    type = register_obj[3]
    cmd_tuple = (run_cmd, type, tape_drive, sysip, submit_time, log_path, status)
    file_name = str(uuid.uuid4())
    file_path = os.path.join(os.getcwd(),'temp',file_name)
    file_handler = open(file_path,'wb')
    pickle.dump(cmd_tuple, file_handler)
    file_handler.close()

    return (file_path,file_name)

@logger_util
def append_register_entry(DUG_connection_obj, register_obj):
    (local_path,file_name) = create_a_pickle_file_for_command(register_obj)
    dug_path = DUG_connection_obj.DUG_proj_path
    remote_path = posixpath.join(dug_path, 'register','from_app', file_name)
    DUG_connection_obj.sftp_client.put(local_path, remote_path)
    logger.info("sucessfully transferred: " + local_path)


if __name__ == '__main__':
    main()