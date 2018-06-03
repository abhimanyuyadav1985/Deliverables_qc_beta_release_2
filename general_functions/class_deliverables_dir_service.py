from configuration import *
import posixpath
from dug_ops.DUG_ops import check_generic_path,create_generic_directory
from database_engine.DB_ops import add_deliverable_data_dir,add_deliverable_qc_dir

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class deliverable_dir_service(object):

    def __init__(self,parent,**kwargs):
        self.parent = parent
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj
        self.deliverable = None
        self.parent_dir = posixpath.join(self.DUG_connection_obj.DUG_proj_path,deliverables_dir)
        self.create_directory(self.parent_dir,"The deliverables parent directory")
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_deliverable(self,deliverable):
        self.deliverable = deliverable
        logger.info("The deliverable is now set to : " + self.deliverable.name)
        self.dir_service_setup()

    def dir_service_setup(self):
        self.set_dir_path()
        self.set_dir_names()
        self.set_data_dir_paths()
        self.set_parent_path_for_individual_set()
        self.set_qc_dir_paths()

    def set_dir_path(self):
        dir_name = str(str(self.deliverable.id) + "_"+ self.deliverable.name)
        self.dir_path = posixpath.join(self.parent_dir,dir_name)

    def set_dir_names(self):
        self.qc_sub_dir_list = deliverable_qc_subdirs_dict[self.deliverable.class_d]
        self.data_dir_list = data_dirs_dict[self.deliverable.class_d]

    def set_data_dir_paths(self):
        self.data_dir_path_dict = {}
        for dir_name in self.data_dir_list:
            key = dir_name
            key_data = posixpath.join(self.dir_path,dir_name)
            dict_entry = {key:key_data}
            self.data_dir_path_dict.update(dict_entry)
            if self.deliverable.class_d =='SEGY':
                dir_name = str(str(self.deliverable.id) + "_" + self.deliverable.name)
                root_path = self.DUG_connection_obj.large_files_dir
                full_path = posixpath.join(root_path,dir_name)
                self.data_dir_path_dict.update({'data':full_path})

    def set_parent_path_for_individual_set(self):
        self.set_dir_path_dict = {}
        iterator_max = int(self.deliverable.copies) + 1
        for i in range(1,iterator_max):
            key = i
            dir_name = str("set_" + str(i))
            dir_path = posixpath.join(self.dir_path,dir_name)
            dict_entry = {key:dir_path}
            self.set_dir_path_dict.update(dict_entry)

    def set_qc_dir_paths(self):
        self.qc_dir_path_dict = {}
        iterator_max = int(self.deliverable.copies) + 1
        for i in range(1, iterator_max):
            key = i
            set_parent_path = self.set_dir_path_dict[key]
            set_dict = {}
            for dir_name in self.qc_sub_dir_list:
                key_1 = dir_name
                dir_path = posixpath.join(set_parent_path,dir_name)
                dict_entry = {key_1:dir_path}
                set_dict.update(dict_entry)
            update_entry = {key:set_dict}
            self.qc_dir_path_dict.update(update_entry)

    def check_path(self, path_to_check):
        status = check_generic_path(self.DUG_connection_obj, path_to_check)
        return status

    def create_all_paths(self):
        self.create_deliverable_dir()
        self.create_data_dir()
        self.create_set_directory()
        self.create_qc_subdirectories()

    def add_all_paths_to_db(self):
        self.add_data_paths_to_db()
        self.add_qc_paths_to_db()

    def create_directory(self,path,message):
        status = self.check_path(path)
        if status == 'True':
            logger.info(path + " :The directory already exists..")
        else:
            logger.info("Now creating ::" + message + "::::" + path)
            create_generic_directory(self.DUG_connection_obj, path)

    def create_deliverable_dir(self):
        message = str("parent directory for deliverable : " + self.deliverable.name)
        self.create_directory(self.dir_path,message)

    def create_data_dir(self):
       for key in self.data_dir_path_dict.keys():
           message = str(key + " directory for deliverable : " + self.deliverable.name)
           self.create_directory(self.data_dir_path_dict[key],message)

    def create_set_directory(self):
        for key in self.set_dir_path_dict.keys():
            message = str("parent direcory for set " + str(key) + " for deliverable: " + self.deliverable.name)
            self.create_directory(self.set_dir_path_dict[key],message)

    def create_qc_subdirectories(self):
        for set_no in self.qc_dir_path_dict.keys():
            for key in self.qc_dir_path_dict[set_no].keys():
                message = str("directory :" + key + ' for set no: ' + str(set_no) + " for deliverable : " + self.deliverable.name)
                dict_obj = self.qc_dir_path_dict[set_no]
                path_to_create = dict_obj[key]
                self.create_directory(path_to_create,message)

    def add_data_paths_to_db(self):
        for dir_type in self.data_dir_path_dict.keys():
            # check and add path to dir
            data_dao = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables_data_dir).filter(
                self.db_connection_obj.Deliverables_data_dir.dir_type == dir_type).filter(
                self.db_connection_obj.Deliverables_data_dir.deliverable_id == self.deliverable.id).first()
            if data_dao == None:
                new_dao_data_dir = self.db_connection_obj.Deliverables_data_dir()
                new_dao_data_dir.deliverable_id = self.deliverable.id
                new_dao_data_dir.dir_type = dir_type
                new_dao_data_dir.path = self.data_dir_path_dict[dir_type]
                # print "Now Adding to database : " + self.data_dir_path_dict[dir_type]
                add_deliverable_data_dir(self.db_connection_obj,new_dao_data_dir)
            else:
                pass


    def add_qc_paths_to_db(self):
        for set_no in self.qc_dir_path_dict.keys():
            for dir_type in self.qc_dir_path_dict[set_no].keys():
                new_dao_qc_dir = self.db_connection_obj.Deliverables_qc_dir()
                new_dao_qc_dir.deliverable_id = self.deliverable.id
                new_dao_qc_dir.set_number = set_no
                dict_obj = self.qc_dir_path_dict[set_no]
                new_dao_qc_dir.path = dict_obj[dir_type]
                new_dao_qc_dir.dir_type = dir_type
                add_deliverable_qc_dir(self.db_connection_obj,new_dao_qc_dir)


if __name__ == '__main__':
    pass












