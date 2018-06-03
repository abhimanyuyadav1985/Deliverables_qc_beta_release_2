from sqlalchemy import create_engine,MetaData, Table
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.automap import automap_base
from configuration import conn_config_file, orca_schema_name, deliverables_qc_schema_name,echo_mode
import os
import pickle

class db_connection_obj(object):

    def __init__(self):
        self.initialize_db_engine()
        self.initialize_db_Session()
        self.initialize_db_working_session()
        self.initialize_scoped_session()
        self.initialize_metadata()
        self.initialize_base()
        self.initialize_all_dao()


    def initialize_all_dao(self):
        self.DAO_list = []
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

    def initialize_db_engine(self):
        engine_definition = str("postgresql://fgeo:Polarcus123@127.0.0.1:1111/abhi_038916")
        print "Now setting up DB engine ..",
        #return create_engine(engine_definition)
        self.db_engine =  create_engine(engine_definition, poolclass = QueuePool,echo = echo_mode)
        print "Done....."

    def initialize_db_Session(self):
        print "Now setting up the Session ....",
        self.Session =  sessionmaker(self.db_engine)
        print "Done....."

    def initialize_db_working_session(self):
        self.sess = self.Session()

    def initialize_scoped_session(self):
        print "Now setting up scoped Session...",
        self.scoped_session = scoped_session(self.Session)
        print "Done....."

    def initialize_metadata(self):
        self.metadata_orca = MetaData(schema=orca_schema_name)
        self.metadata_deliverables_qc = MetaData(schema = deliverables_qc_schema_name)

    def initialize_base(self):
        self.Base_orca = automap_base(metadata = self.metadata_orca)
        self.Base_orca.prepare(self.db_engine, reflect=True)
        self.Base_deliverables_qc = automap_base(metadata = self.metadata_deliverables_qc)
        self.Base_deliverables_qc.prepare(self.db_engine, reflect=True)

    def initialize_dao_project_info(self):
        print "Now setting up DAO for Project info....",
        self.Project_info = self.Base_orca.classes.project_info
        self.DAO_list.append('Project_info')
        print "Done......."

    def initialize_dao_deliverables_definition(self):
        self.Deliverables_def = Table('deliverables',self.metadata_deliverables_qc,autoload = True,autoload_with =self.db_engine)

    def initialize_dao_deliverables(self):
        print "Now setting up DAO for deliverables table....",
        self.Deliverables =  self.Base_deliverables_qc.classes.deliverables
        self.DAO_list.append('Deliverables')
        print "Done......."

    def initialize_dao_deliverables_data_dir(self):
        print "Now setting up DAO for deliverables data dir table....",
        self.Deliverables_data_dir = self.Base_deliverables_qc.classes.deliverables_data_dir
        self.DAO_list.append('Deliverables_data_dir')
        print "Done......."

    def initialize_dao_deliverables_qc_dir(self):
        print "Now setting up DAO for deliverables qc dir table....",
        self.Deliverables_qc_dir = self.Base_deliverables_qc.classes.deliverables_qc_dir
        self.DAO_list.append('Deliverables_qc_dir')
        print "Done......."

    def initialize_dao_raw_seq_info(self):
        print "Now setting up DAO for Raw seq info table....",
        self.Raw_seq_info = self.Base_deliverables_qc.classes.raw_seq_info
        self.DAO_list.append('Raw_seq_info')
        print "Done......."

    def initialize_dao_shipments(self):
        print "Now setting up DAO for shipments table....",
        self.Shipments = self.Base_deliverables_qc.classes.shipment_entries
        self.DAO_list.append('Shipments')
        print "Done......."

    def initialize_dao_tape(self):
        print "Now setting up DAO for orca SEGD tape table ......",
        self.SEGD_tapes = self.Base_orca.classes.tape
        self.DAO_list.append('SEGD_tapes')
        print "Done ......"

    def initialize_dao_segd_qc(self):
        print "Now setting up DAO for orca SEGD tape QC table ......",
        self.SEGD_qc = self.Base_deliverables_qc.classes.segd_qc
        self.DAO_list.append('SEGD_qc')
        print "Done ......"

    def initialize_dao_media_list(self):
        print "Now adding the DAO for media list table .....",
        self.Media_list = self.Base_deliverables_qc.classes.media_list
        self.DAO_list.append('Media_list')
        print "Done .... "

    def initialize_dao_usb_list(self):
        print "Now adding the DAO for usb list table .... ",
        self.USB_list = self.Base_deliverables_qc.classes.usb_list
        self.DAO_list.append('USB_list')
        print "Done ...."

    def initialize_dao_usb_files(self):
        print "Now adding the DAO for usb files list table ....",
        self.USB_files = self.Base_deliverables_qc.classes.usb_files
        self.DAO_list.append('USB_files')
        print "Done ...."

    def initialize_dao_change_log(self):
        print "Now adding DAO for change log table .....",
        self.change_log = self.Base_deliverables_qc.classes.change_log
        self.DAO_list.append('change_log')
        print "Done ..."

    def initialize_dao_line(self):
        print "Now adding DAO for change line table .....",
        self.Line = self.Base_orca.classes.line
        self.DAO_list.append('Line')
        print "Done ..."

    def initialize_dao_seq_segy_qc_on_disk(self):
        print "Now adding DAO for change SEGY on disk QC  table .....",
        self.SEGY_QC_on_disk = self.Base_deliverables_qc.classes.seq_segy_qc_on_disk
        self.DAO_list.append('SEGY_QC_on_disk')
        print "Done ..."

    def initialize_dao_segy_write(self):
        print "Now adding DAO for SEGY write Table ...",
        self.SEGY_write = self.Base_deliverables_qc.classes.segy_write
        self.DAO_list.append('SEGY_write')
        print "Done ..."


class DAO_table_obj(object):
    def __init__(self, initial_data):
        for a_key in initial_data:
            setattr(self,a_key,initial_data[a_key])


def main():
    db_obj = db_connection_obj()
    db_obj_dict = db_obj.__dict__
    initial_data_dict = {}
    for a_key in db_obj.DAO_list:
         initial_data_dict.update({a_key : db_obj_dict[a_key].__table__.columns.__str__()})
    DAO_obj = DAO_table_obj(initial_data_dict)
    print DAO_obj.__dict__
    file_name = 'Expected_table_setup.tbc'
    file_path = os.path.join(os.getcwd(),file_name)
    file_handler = open(file_path,'wb')
    pickle.dump(DAO_obj,file_handler)
    file_handler.close()



if __name__ == "__main__":
    main()

