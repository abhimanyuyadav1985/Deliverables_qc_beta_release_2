import posixpath
from PyQt4 import QtCore
import time
from dug_ops.DUG_ops import check_generic_path
import os
import pickle
from configuration import conn_config_file
import paramiko

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class run_information_sync(QtCore.QObject):

    doingWork = QtCore.pyqtSignal(bool, str, str)
    cmdcontrol = QtCore.pyqtSignal(str)
    update_tape_dashboard = QtCore.pyqtSignal()

    def __init__(self,dug_proj_path,thread_name):
        super(run_information_sync,self).__init__()
        self.thread_name = thread_name
        self.DUG_proj_path = dug_proj_path
        self.DUG_connection_obj = thread_DUG_client()


    def run_and_flush(self):
        while True:
            self.import_task_log()
            time.sleep(31)


    def create_busy_device_list(self):
        busy_dev_path = os.path.join(os.getcwd(),'temp','active_tasks')
        if os.path.exists(busy_dev_path):
            os.remove(busy_dev_path)
        else:
            logger.info("Creating busy devices file : " + busy_dev_path)
            file_handler = open(busy_dev_path, 'wb')
            pickle.dump(self.task_dict, file_handler)
            file_handler.close()
            logger.info("Done ...")
            self.update_tape_dashboard.emit()


    def import_task_log(self):
        self.doingWork.emit(True, "Importing task log", self.thread_name)
        proj_path = self.DUG_proj_path
        remote_path = posixpath.join(proj_path, 'register', 'active_tasks')
        remote_lock_path = posixpath.join(proj_path,'register','app_task_sync_lock')

        local_path = os.path.join(os.getcwd(), 'temp', 'active_tasks')
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception as error:
                logger.error("Exception: Local task_log_busy waiting 7s")
                logger.error(error)
                self.doingWork.emit(True, "Exception: Local task_log_busy waiting 7s", self.thread_name)
                time.sleep(7)
                self.import_task_log()
        status_lock = check_generic_path(self.DUG_connection_obj,remote_lock_path)
        if status_lock == 'True':
            logger.warning("Deliverables QC daemon is writing to file, wait 5s")
            self.doingWork.emit(True, "Deliverables QC daemon is writing to file, wait 5s", self.thread_name)
            time.sleep(5)
            self.import_task_log()
        else:
            status = check_generic_path(self.DUG_connection_obj, remote_path)
            if status == 'True':
                # Now FTP the file
                logger.info("Now copying over the task log from remote host ..")
                self.doingWork.emit(True, "Now copying over the task log from remote host ..", self.thread_name)
                try:
                    self.DUG_connection_obj.sftp_client.get(remote_path, local_path)
                    logger.info('Done ..')
                    self.local_path = local_path
                    self.extract_task_info()
                except Exception as error:
                    logger.error("Exception: Unable to copy to local host ")
                    logger.error(error)
                    self.doingWork.emit(True, "Exception: Unable to copy to local host ", self.thread_name)
            else:
                logger.info("No active tasks on  remote host..")
                self.doingWork.emit(True, "No active tasks on  remote host..", self.thread_name)


    def extract_task_info(self):
        file_handler = open(self.local_path, 'rb')
        self.task_dict = pickle.load(file_handler)
        file_handler.close()
        if len(self.task_dict.keys()) == 0:
            logger.info("No active tasks available")
        else:
            self.create_busy_device_list()



class thread_DUG_client(object):
    def __init__(self):
        file_path = os.path.join(os.getcwd(),
                                 conn_config_file)  # use this string for production mode in the application

        file_handler = open(file_path, 'rb')
        obj_config = pickle.load(file_handler)
        file_handler.close()
        host = obj_config.DUG_IP
        port = 22
        DUG_user = obj_config.DUG_user
        DUG_pword = obj_config.DUG_pword
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=DUG_user, password=DUG_pword)
        logger.info("Transport for DUG connection now setup..")
        self.ws_client = paramiko.SSHClient()
        self.ws_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ws_client.connect(host, username=DUG_user, password=DUG_pword)
        logger.info("The DUG WS client is now active ..")
        self.sftp_client = paramiko.SFTPClient.from_transport(self.transport)
        logger.info("The DUG sftp client is now active .. ")





