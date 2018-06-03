from general_functions.general_functions import get_item_through_dialogue
from database_engine.DB_ops import get_list_of_segd_deliverables
from general_functions.class_deliverables_dir_service_through_db import deliverable_dir_service_through_db
from general_functions.class_deliverables_dir_service import deliverable_dir_service
from general_functions.class_deliverables_file_service import deliverable_file_service
from Tape_services.class_SEGY_service import SEGY_service
from Tape_services.class_SEGD_QC_service import SEGD_QC_service
from Tape_services.class_Tape_service import Tape_service
from database_engine.DB_ops import get_all_SEGY_deliverable_for_tape_write

import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class Tape_operation_manager(object):

    def __init__(self,parent):

        self.parent = parent

        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj

        self.use_location = self.parent.use_location

        self.dir_service = deliverable_dir_service_through_db(self)
        self.file_service = deliverable_file_service(self)

        self.tape_service = Tape_service(self)

        self.deliverable = None

    def get_verified_tape_drive(self,GUI_object):
        top_message = 'Tape drive'
        message = 'Please enter the tape drive name'
        typed_tape_drive = get_item_through_dialogue(GUI_object,top_message)
        if typed_tape_drive is not None:
            if typed_tape_drive in self.tape_service.available_dst:
                self.set_tape_drive(typed_tape_drive)
                return True
            else:
                logger.warning("The specified tape drive does not exist")
                self.get_verified_tape_drive(GUI_object)


    def set_tape_drive(self, tape_drive):
        self.tape_drive = tape_drive
        logger.info("The tape drive is now set to :: " + self.tape_drive)

    def get_verified_set(self,GUI_object):
        top_message = "Set number"
        message = "Please enter the set number"
        typed_set_number = get_item_through_dialogue(GUI_object,top_message)
        if typed_set_number is not None:
            if int(typed_set_number) in range(1,int(self.deliverable.copies) + 1):
               self.set_working_set(typed_set_number)
               return True
            else:
                logger.warning("The entered set number is not in range")
                self.get_verified_set(GUI_object)

    def set_working_set(self, set_number):
        self.set_no = str(set_number)
        logger.info("The tape operation service working set is now :: " + str(self.set_no))



    def set_deliverable(self, deliverable_name):
        self.deliverable = self.deliverable_dict[deliverable_name]
        self.dir_service.set_deliverable(self.deliverable)
        self.file_service.set_deliverable(self.deliverable)
        logger.info("Tape operation serivce Deliverable is now set to:: " + self.deliverable.name)
        self.set_service_class_name(self.deliverable.class_d)

    def set_service_class_name(self, service_class_name):
        self.service_class_name = service_class_name
        self.set_service_class()

    def set_service_class(self):
        if self.service_class_name == 'SEGD':
            self.service_class = SEGD_QC_service(self)
        else:
            self.service_class = SEGY_service(self)
        logger.info("The tape operation service is not set to :: " + self.service_class.name)


    def set_seq_name(self,name):
        self.seq_name = name

    def set_tape_name(self,tape_name):
        self.tape_name = tape_name
        if self.service_class_name == 'SEGD':
            self.service_class.set_min_max_ffid()
        else:
            self.service_class.set_tape_name(tape_name)

    def get_available_segd_deliverable_list(self):
        list = get_list_of_segd_deliverables(self.db_connection_obj)
        combo_item_list = []
        self.deliverable_dict = {}
        for deliverable in list:
            combo_item_list.append(deliverable.name)
            dict_entry = {deliverable.name : deliverable}
            self.deliverable_dict.update(dict_entry)
        return combo_item_list


    def get_deliverable_set_list(self):
        combo_list = []
        for i in range(1, int(self.deliverable.copies)+1):
            combo_list.append(str(i))
        return combo_list

    def get_confirmation_for_tape_label(self,GUI_object):
        top_message = "Please enter the tape label manually for check"
        typed_label = get_item_through_dialogue(GUI_object, top_message)
        return typed_label


    def get_all_SEGY_tape_write_deliverable_list(self):
        list = get_all_SEGY_deliverable_for_tape_write(self.db_connection_obj)
        combo_item_list = []
        self.deliverable_dict = {}
        for deliverable in list:
            combo_item_list.append(deliverable.name)
            dict_entry = {deliverable.name: deliverable}
            self.deliverable_dict.update(dict_entry)
        return combo_item_list







