from sqlalchemy import create_engine,MetaData, Table
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker,scoped_session
import pickle
from sqlalchemy.ext.automap import automap_base
from configuration import conn_config_file, orca_schema_name, deliverables_qc_schema_name,echo_mode
import os,sys

from sqlalchemy import event
from sqlalchemy.engine import Engine

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

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("Start Query: %s" % statement)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Query Complete!")
    logger.debug("Total Time: %f" % total)


class db_connection_obj(object):

    def __init__(self):
        self.initialize_db_engine()
        if self.db_engine_status ==True:
            self.initialize_db_Session()
            self.initialize_db_working_session()
            self.initialize_scoped_session()
            self.initialize_metadata()
            self.initialize_base()
            self.initialize_all_dao()
        else:
            logger.error("Cannot proceed as the the database engine is not setup")


    def initialize_all_dao(self):
        self.initialize_dao_project_info()
        self.initialize_dao_deliverables_definition()
        self.initialize_dao_deliverables()
        self.initialize_dao_deliverables_data_dir()
        self.initialize_dao_deliverables_qc_dir()
        self.initialize_dao_raw_seq_info()
        self.initialize_dao_shipments()
        self.initialize_dao_tape()
        self.initialize_dao_segd_qc()
        self.initialize_dao_media_list()
        self.initialize_dao_usb_list()
        self.initialize_dao_usb_files()
        self.initialize_dao_change_log()
        self.initialize_dao_line()
        self.initialize_dao_seq_segy_qc_on_disk()
        self.initialize_dao_segy_write()

    
    @logger_util
    def initialize_db_engine(self):
        #file_path = os.path.join(Path(os.getcwd()).parent, conn_config_file) # use this string to test the stand alone connection module
        file_path = os.path.join(os.getcwd(), conn_config_file) # use this string for production mode in the application
        logger.info("config_file: " + file_path)
        file_handler = open(file_path, "rb")
        obj= pickle.load(file_handler)
        file_handler.close()
        db_name = obj.db_name
        db_user = obj.db_user
        db_pword = obj.db_pword
        db_port = obj.db_port
        self.db_name = db_name
        host_IP = obj.host_IP
        host_user = obj.host_user
        host_pword = obj.host_pword
        # with SSHTunnelForwarder((host_IP, 22), ssh_password=host_pword, ssh_username=host_user,
        #                         remote_bind_address=('127.0.0.1', 5432),local_bind_address=('0.0.0.0', 1111))as server:
        engine_definition = str('postgresql://'+ db_user + ":"+db_pword + "@127.0.0.1:1111/"+db_name)
        #return create_engine(engine_definition)
        try:
            self.db_engine =  create_engine(engine_definition, poolclass = QueuePool,echo = echo_mode)
            self.db_engine_status = True
        except Exception as error:
            logger.critical(error)
            self.db_engine_status = False
            logger.critical("Exiting application since it cannot conenct to Db")
            sys.exit()

    
    @logger_util
    def initialize_db_Session(self):
        try:
            self.Session =  sessionmaker(self.db_engine)
        except Exception as e:
            logger.critical("Unable to setup db_session")

    
    @logger_util
    def initialize_db_working_session(self):
        try:
            self.sess = self.Session()
        except Exception as error:
            logger.critical(error)

    
    @logger_util
    def initialize_scoped_session(self):
        try:
            self.scoped_session = scoped_session(self.Session)
        except Exception as error:
            logger.critical(error)

    
    @logger_util
    def initialize_metadata(self):
        try:
            self.metadata_orca = MetaData(schema=orca_schema_name)
            self.metadata_deliverables_qc = MetaData(schema = deliverables_qc_schema_name)
            self.metadta_public = MetaData(schema = 'public')
        except Exception as error:
            logger.critical(error)

    
    @logger_util
    def initialize_base(self):
        try:

            self.Base_orca = automap_base(metadata = self.metadata_orca)
            self.Base_deliverables_qc = automap_base(metadata=self.metadata_deliverables_qc)
            self.Base_public = automap_base(metadata = self.metadta_public)

            self.Base_orca.prepare(self.db_engine, reflect=True)
            self.Base_deliverables_qc.prepare(self.db_engine, reflect=True)
            self.Base_public.prepare(self.db_engine, reflect = True)


        except Exception as error:
            logger.critical(error)

    
    @logger_util
    def initialize_dao_project_info(self):
        try:
            self.Project_info = self.Base_orca.classes.project_info
        except Exception as error:
            logger.error(error)

    def initialize_dao_deliverables_definition(self):
        self.Deliverables_def = Table('deliverables',self.metadata_deliverables_qc,autoload = True,autoload_with =self.db_engine)

    
    @logger_util
    def initialize_dao_deliverables(self):
        try:
            self.Deliverables =  self.Base_deliverables_qc.classes.deliverables
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_deliverables_data_dir(self):
        try:
            self.Deliverables_data_dir = self.Base_deliverables_qc.classes.deliverables_data_dir
        except Exception as error:
            logging.error(error)

    
    @logger_util
    def initialize_dao_deliverables_qc_dir(self):
        try:
            self.Deliverables_qc_dir = self.Base_deliverables_qc.classes.deliverables_qc_dir
        except Exception as error:
            logging.error(error)

    
    @logger_util
    def initialize_dao_raw_seq_info(self):
        try:
            self.Raw_seq_info = self.Base_public.classes.raw_seq_info
        except Exception as error:
            logging.error(error)

    
    @logger_util
    def initialize_dao_shipments(self):
        try:
            self.Shipments = self.Base_deliverables_qc.classes.shipment_entries
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_tape(self):
        try:
            self.SEGD_tapes = self.Base_orca.classes.tape
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_segd_qc(self):
        try:
            self.SEGD_qc = self.Base_deliverables_qc.classes.segd_qc
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_media_list(self):
        try:
            self.Media_list = self.Base_deliverables_qc.classes.media_list
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_usb_list(self):
        try:
            self.USB_list = self.Base_deliverables_qc.classes.usb_list
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_usb_files(self):
        try:
            self.USB_files = self.Base_deliverables_qc.classes.usb_files
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_change_log(self):
        try:
            self.change_log = self.Base_deliverables_qc.classes.change_log
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_line(self):
        try:
            self.Line = self.Base_orca.classes.line
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_seq_segy_qc_on_disk(self):
        try:
            self.SEGY_QC_on_disk = self.Base_deliverables_qc.classes.seq_segy_qc_on_disk
        except Exception as error:
            logger.error(error)

    
    @logger_util
    def initialize_dao_segy_write(self):
        try:
            self.SEGY_write = self.Base_deliverables_qc.classes.segy_write
        except Exception as error:
            logger.error(error)


if __name__ == "__main__":
    pass

