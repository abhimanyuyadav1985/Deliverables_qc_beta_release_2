import sys
import os
import pickle
import time
from datetime import datetime


task_lock_name = 'task_lock'
task_log_name = 'task_log'
task_finished_name = 'finished_task_log'
lock_name = 'status_update_lock'
log_name = 'task_manager_execution_summary'

def main():
    "check is task mover execution summary exists"
    log_path = os.path.join(str(sys.argv[1]),log_name)
    if os.path.exists(log_path):
        pass
    else:
        file_handler = open(log_path,'wb')
        file_handler.write(str("New log created on : " + str(datetime.now()) + '\n'))
        file_handler.close()
    # check is the task log lock is enabled
    status_lock_path = os.path.join(str(sys.argv[1]),lock_name)
    path_name_lock = os.path.join(str(sys.argv[1]),task_lock_name)
    check_lock_state(path_name_lock)
    path_name_task_log = os.path.join(str(sys.argv[1]),task_log_name)
    path_name_finished_log = os.path.join(str(sys.argv[1]),task_finished_name)
    manupulate_lock_state('create',status_lock_path)
    file_handler = open(path_name_task_log,'rb')
    running_task_list = pickle.load(file_handler)
    file_handler.close()
    manupulate_lock_state('remove',status_lock_path)
    for a_task in running_task_list:
        if a_task[1] == 'segy_qc':
            previous_state = a_task[3]
        cmd = str("ps -ef")
        cmd_out = os.popen(cmd).readlines()
        if a_task[3] == 'new':
            a_task[3] = 'try_1'
        elif a_task[3] == 'try_1':
            a_task[3] ='try_2'
        else:
            a_task[3] = 'Finished'

        for a_line in cmd_out:
            if str(a_task[2]) in a_line:
                a_task[3] = 'Running'

        if a_task[1] == 'segy_qc':
            current_state = a_task[3]
            if previous_state == 'Running' and current_state == 'Finished':
                if os.path.exists(os.path.join(str(sys.argv[1]), 'segy_qc_lock')):
                    os.remove(os.path.join(str(sys.argv[1]), 'segy_qc_lock'))

    manupulate_lock_state('create', status_lock_path)
    os.remove(path_name_task_log)
    file_handler = open(path_name_task_log,'wb')
    pickle.dump(running_task_list,file_handler)
    file_handler.close()
    manupulate_lock_state('remove',status_lock_path)


    if sys.argv[2] == 'flush':
        manupulate_lock_state('create',status_lock_path)
        move_finished_to_finish_log(path_name_task_log,path_name_finished_log,log_path)
        manupulate_lock_state('remove',status_lock_path)
    else:
        pass


def move_finished_to_finish_log(running_log_path,finished_log_path,log_path):
    file_handler = open(running_log_path,'rb')
    current_task_list = pickle.load(file_handler)
    file_handler.close()
    for a_task in current_task_list:
        if a_task[3] == 'Finished':
            current_task_list.remove(a_task)
            string_to_print = str('Moving to Finished : ' + a_task[0])
            add_to_finished_log(finished_log_path,a_task)
            print_to_log(log_path,string_to_print)
    print_to_log(log_path, 'Removing old log')
    os.remove(running_log_path)
    file_handler = open(running_log_path,'wb')
    pickle.dump(current_task_list,file_handler)
    file_handler.close()


def add_to_finished_log(finished_log_path,a_task):
    if os.path.exists(finished_log_path):
        pass
    else:
        file_h = open(finished_log_path,'wb')
        file_h.write(" \n")
        file_h.close()
    file_h = open(finished_log_path,'a')
    file_h.write(str(a_task[0]))
    file_h.write("\n")
    file_h.close()


def manupulate_lock_state(action,lock_path):
    if action == 'create':
        file_handler = open(lock_path, 'wb')
        file_handler.write("")
        file_handler.close()
    else:
        os.remove(lock_path)

def check_lock_state(path_name):
    if os.path.exists(path_name):
        time.sleep(10)
        check_lock_state(path_name)
    else:
        return None

def print_to_log(log_path, string_to_print):
    file_log = open(log_path,'a')
    string_for_log = str(datetime.now()) + " :: " + string_to_print + ' \n'
    file_log.write(string_for_log)
    file_log.close()


if __name__ == '__main__':
    main()



















