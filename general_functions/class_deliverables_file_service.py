from database_engine.DB_ops import get_segd_qc_path
import posixpath

class deliverable_file_service(object):
    def __init__(self,parent):
        self.parent = parent
        self.dir_service = self.parent.dir_service

    def set_deliverable(self,deliverable):
        self.deliverable = deliverable
        self.deliverable_class_d_name = self.deliverable.class_d
        self.deliverable_type_name = self.deliverable.type

    def get_segd_wc_logfile_path(self):
        search_obj = get_segd_qc_path(self.parent.db_connection_obj,self.parent.deliverable.id,self.parent.set_no)
        path = search_obj.path
        return path

    def set_segd_log_file_path(self):
        dir_path = self.get_segd_wc_logfile_path()
        file_name = self.parent.seq_name + "--" + self.parent.tape_name + "--set" + self.parent.set_no +'.log'
        log_file_path = posixpath.join(dir_path,file_name)
        return log_file_path

    def return_encoded_string(self,file_path):
        cmd = str('python /d/home/share/bin/base_64_encoder.py ' + file_path)
        stdin, stdout, stderr = self.parent.DUG_connection_obj.ws_client.exec_command(cmd)
        # std_out = []
        # for line in  stdout.readlines():
        #     std_out.append(line)
        # return std_out[0]
        return stdout.read()

if __name__ == '__main__':
    pass

