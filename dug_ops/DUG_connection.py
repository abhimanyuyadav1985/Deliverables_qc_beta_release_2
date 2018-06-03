import pickle
import pickle,paramiko,os
from configuration import conn_config_file,Tape_server_dict
from dug_ops.DUG_ops import transfer_SEGY_check_script

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class DUG_connection_object(object):

    def __init__(self,use_env):

        self.large_files_dir = None
        self.DUG_proj_name()
        self.DUG_project_path()
        self.set_transport()
        self.DUG_ws_client()
        self.use_env = use_env
        self.DUG_tape_server_client()
        self.DUG_sftp_client()
        #self.transfer_SEGY_checking_package()

    def DUG_proj_name(self):
        file_path = os.path.join(os.getcwd(),
                                 conn_config_file)  # use this string for production mode in the application

        file_handler = open(file_path, 'rb')
        obj_config = pickle.load(file_handler)
        file_handler.close()
        self.DUG_project_name = obj_config.db_name
        logger.info("The DUG project name is set to : " + str(self.DUG_proj_name))

    def DUG_project_path(self):
        file_path = os.path.join(os.getcwd(),
                                 conn_config_file)  # use this string for production mode in the application
        file_handler = open(file_path, 'rb')
        obj_config = pickle.load(file_handler)
        file_handler.close()
        self.DUG_proj_path = obj_config.DUG_segy_path
        logger.info("The DUG project path is set to: " + self.DUG_proj_path)

    def set_transport(self):
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


    def DUG_ws_client(self):
        file_path = os.path.join(os.getcwd(),
                                     conn_config_file)  # use this string for production mode in the application

        file_handler = open(file_path, 'rb')
        obj_config = pickle.load(file_handler)
        file_handler.close()
        host = obj_config.DUG_IP
        port = 22
        DUG_user = obj_config.DUG_user
        DUG_pword = obj_config.DUG_pword
        self.ws_client = paramiko.SSHClient()
        self.ws_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ws_client.connect(host, username=DUG_user, password=DUG_pword)
        logger.info("The DUG WS client is now active ..")


    def DUG_tape_server_client(self):
        file_path = os.path.join(os.getcwd(),
                                 conn_config_file)  # use this string for production mode in the application
        file_handler = open(file_path, 'rb')
        obj_config = pickle.load(file_handler)
        file_handler.close()
        host = Tape_server_dict[self.use_env]
        DUG_user = obj_config.DUG_user
        DUG_pword = obj_config.DUG_pword
        self.ts_client = paramiko.SSHClient()
        self.ts_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ts_client.connect(host, username=DUG_user, password=DUG_pword)
        logger.info("The DUG tape server client is now active ..")


    def DUG_sftp_client(self):
        file_path = os.path.join(os.getcwd(),
                                 conn_config_file)  # use this string for production mode in the application
        file_handler = open(file_path, 'rb')
        obj_config = pickle.load(file_handler)
        file_handler.close()
        host = obj_config.DUG_IP
        port = 22
        DUG_user = obj_config.DUG_user
        DUG_pword = obj_config.DUG_pword
        dug_path = obj_config.DUG_segy_path
        project_name = obj_config.db_name
        self.sftp_client = paramiko.SFTPClient.from_transport(self.transport)
        logger.info("The DUG sftp client is now active .. ")


    def transfer_SEGY_checking_package(self):
        transfer_SEGY_check_script(self)


if __name__ == "__main__":
    pass

