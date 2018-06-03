from configuration import *
from dug_ops.DUG_ops import run_command_on_tape_server
import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

class Tape_service(object):
    def __init__(self,parent):

        self.parent = parent

        self.use_location = self.parent.use_location

        self.DUG_connection_obj = self.parent.DUG_connection_obj
        self.db_connection_obj = self.parent.db_connection_obj

        self.set_available_dst()
        self.set_status_command_dict()
        self.set_rewind_command_dict()
        self.set_eject_command_dict()

    def run_cmd(self,cmd,dev_to_use):
        logger.info(cmd)
        run_command_on_tape_server(self.DUG_connection_obj,cmd,dev_to_use)


    def set_available_dst(self):
        self.available_dst = location_wise_tape_driver_dict[self.use_location]

    def set_status_command_dict(self):
        self.dst_status_command_dict = {}
        for dst in self.available_dst:
            new_dict_key = dst
            new_dict_ket_cmd = str("mt -t /dev/" + new_dict_key + " status")
            new_dict_entry = {new_dict_key:new_dict_ket_cmd}
            self.dst_status_command_dict.update(new_dict_entry)

    def set_rewind_command_dict(self):
        self.dst_rewind_command_dict = {}
        for dst in self.available_dst:
            new_dict_key = dst
            new_dict_ket_cmd = str("mt -t /dev/" + new_dict_key + " rewind")
            new_dict_entry = {new_dict_key: new_dict_ket_cmd}
            self.dst_rewind_command_dict.update(new_dict_entry)

    def set_eject_command_dict(self):
        self.dst_eject_command_dict = {}
        for dst in self.available_dst:
            new_dict_key = dst
            new_dict_ket_cmd = str("mt -t /dev/" + new_dict_key + " eject")
            new_dict_entry = {new_dict_key: new_dict_ket_cmd}
            self.dst_eject_command_dict.update(new_dict_entry)


if __name__ =="__main__":
    test = Tape_service("Asima")
    print test.available_dst
    print test.dst_status_command_dict
    print test.dst_rewind_command_dict
    print test.dst_eject_command_dict





