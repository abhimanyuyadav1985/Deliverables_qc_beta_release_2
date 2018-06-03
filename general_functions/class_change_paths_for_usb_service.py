from class_deliverables_dir_service import deliverable_dir_service

class change_usb_deliverable_paths(object):

    def __init__(self, parent,usb_d,ref_d):
        # define the top window

        super(change_usb_deliverable_paths, self).__init__()
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj
        self.DUG_connection_obj = self.parent.DUG_connection_obj

        self.dir_service = deliverable_dir_service(self)

        self.dir_service.set_deliverable(ref_d)

        self.ref_data_dir_path_dict = self.dir_service.data_dir_path_dict

        self.dir_service.set_deliverable(usb_d)

        self.usb_data_dir_path_dict = self.dir_service.data_dir_path_dict
        self.usb_qc_dir_path_dict = self.dir_service.qc_dir_path_dict

        self.search_and_replace_all_paths()


    def search_and_replace_all_paths(self):
        self.search_and_replace_data_paths()
        self.search_and_delete_qc_paths()



    def search_and_replace_data_paths(self):
        for key in self.usb_data_dir_path_dict.keys():
            new_obj = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables_data_dir).filter(self.db_connection_obj.Deliverables_data_dir.path == self.usb_data_dir_path_dict[key]).first()
            new_obj.path = self.ref_data_dir_path_dict[key]
            self.db_connection_obj.sess.commit()



    def search_and_delete_qc_paths(self):
        for key in self.usb_qc_dir_path_dict.keys():
            for key2 in self.usb_qc_dir_path_dict[key].keys():
                search_dict = self.usb_qc_dir_path_dict[key]
                print search_dict[key2]
                new_obj = self.db_connection_obj.sess.query(self.db_connection_obj.Deliverables_qc_dir).filter(self.db_connection_obj.Deliverables_qc_dir.path == search_dict[key2])
                new_obj.delete()
                self.db_connection_obj.sess.commit()












































