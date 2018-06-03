from configuration import *
import posixpath

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class deliverable_dir_service_through_db(object):

    def __init__(self,parent,**kwargs):
        self.parent = parent
        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj
        self.deliverable = None
        self.parent_dir = posixpath.join(self.DUG_connection_obj.DUG_proj_path,deliverables_dir)

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
        data_path_from_db_list = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables_data_dir).filter(
            self.db_connection_obj.Deliverables_data_dir.deliverable_id == self.deliverable.id).all()
        for item in data_path_from_db_list:
            key = item.dir_type
            data = item.path
            self.data_dir_path_dict.update({key:data})

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

if __name__ == '__main__':
    pass












