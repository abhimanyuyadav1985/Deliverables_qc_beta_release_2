import sqlite3
import sys
import logging
import time
import os
import pickle

class Task_execution_service(object):
    """
    Task execution service running on the DUG tape server

    """

    def __init__(self, log_path, database_path):
        
        self.setup_logging(log_path)
        self.database_connection = False
        self.create_database_connection(database_path)


    def setup_logging(self,log_path):
        """
        logging function for the task execution service
        :param log_path: log file used by the loggin service
        :return: None

        """
        self.logging = logging
        self.logging.basicConfig(level=logging.DEBUG,
                                 format='%(asctime)s %(levelname)-8s %(message)s',
                                 datefmt='%a, %d %b %Y %H:%M:%S',
                                 filename=log_path,
                                 file_mode = 'w')
        self.logging.info('Logging services setup done ....')


    
    def create_database_connection(self,database_path):
        """
        create the database connection to the specified SQLite database file
        :param database_path: path to the project SQLlite data
        :return: change the parameter self.database connection to true when connected to the database
        """
        if os.path.exists(database_path):
            self.logging.info('Found file now connecting to database: ' + database_path)
            try:
                self.conn = sqlite3.connect(database_path, isolation_level = None)
                self.cursor = self.conn.cursor()
                self.logging.info("Done.. ")
                self.database_connection = True
            except Exception as e:
                self.logging.error('Unable to connect to database')
                self.logging.error(e)
        else:
            self.logging.error("Unable to locate database file")
            

    def add_new_commands_to_database(self):
        """
        Check the fole ../from_app

        This is the folder when the pickle files for the commands from the deliverables qc application are sent
        :return: none
        """
        try:
            self.logging.info('Now looking for commands to add to database')
            app_command_dir = os.path.join(os.getcwd(),'from_app')
            cmds_to_add = os.listdir(app_command_dir)
            if len(cmds_to_add) ==0:
                self.logging.info("No new commands to add to the database")
            else:
                for a_cmd in cmds_to_add:
                    self.logging.info('Found: ' + a_cmd)
                    cmd_path = os.path.join(app_command_dir, a_cmd)
                    self.add_single_cmd(cmd_path)
                self.logging.info("Addition of new commands to the database complete") 
        except Exception as e:
            self.logging.error(e)
            
    def add_single_cmd(self, cmd_path):
        """
        Add a single command from the pickle file to the database and add to logfile
        :param cmd_path: path to the pickle file to be added to the database as a command
        :return:
        """
        try:
            file_handler = open(cmd_path, 'rb')
            cmd_tuple_to_use = pickle.load(file_handler)
            file_handler.close()
            self.cursor.execute('INSERT INTO tasks(command,type,drive,sysip,submittime,logpath,status) VALUES(?,?,?,?,?,?,?)', cmd_tuple_to_use)
            self.conn.commit()
            self.logging.info('Added to database: ' + cmd_path)
            os.remove(cmd_path)
        except Exception as e:
            self.logging.error(e)

            
    def submitted_job_status_sync(self):
        """
        Sync the status for tasks with status submit, unsure, doubt and active

        submit -> unsure if missing in ps-ef or active if present

        unsure -> doubt if missing in ps -ef or active if present

        doubt -> error if missing in ps -ef or active if present

        unsure or doubt are used because some of the tape tasks do not start instantly and we may need to wait for sometime before dismissing them as errored
        :return: None
        """
        try:
            submitted_job_status_dict = {'submit' : 'unsure','unsure': 'doubt','doubt': 'error','active': 'finished'}
            self.logging.info("Now syncing submitted job status")
            self.cursor.execute("SELECT * FROM tasks WHERE status in ('submit','unsure','doubt','active')")
            self.submit_tasks = self.cursor.fetchone()
            if self.submit_tasks == None:
                self.logging.info("No jobs with status: submit,doubt or unsure")
            else:
                for a_task in self.submit_tasks:
                    (id,command,type,drive,sysip,submittime,status,logpath,exe_time,finish_time,exception) = a_task
                    cmd = str("ps -ef")
                    cmd_out = os.popen(cmd).readlines()
                    new_status = submitted_job_status_dict[status]
                    for a_line in cmd_out:
                        if command in a_line:
                            new_status = 'active'

                    if new_status == 'finished': # finish_time needs to be added to the job when it finishes
                        finish_time = time.strftime("%Y%m%d-%H%M%S")
                        self.cursor.execute('UPDATE tasks SET status = ? , finish_time = ? WHERE id= ?', (new_status, finish_time, id))
                    else: # no need to add finish_time when the job is not finished
                        self.cursor.execute('UPDATE tasks SET status = ? WHERE id= ?',(new_status,id))
                    self.logging.info('Status for task id: ' + id + ' Changed from : '+ status + ' to: ' + new_status )
                    if type == 'segy_qc'and new_status == 'finished': # management of segy_qc_lock
                        if os.path.exists(os.path.join(os.getcwd(),'segy_qc_lock')):
                            try:
                                os.remove(os.path.join(os.getcwd(),'segy_qc_lock'))
                                self.logging.info("SEGY QC lock removed for task id: " + id)
                            except Exception as e:
                                self.logging.error(e)

        except Exception as e:
            self.logging.error(e)
            
    
    def submit_new_jobs(self):
        """
        Check the availability of resources and submit queued jobs to the tape server

        Execute only one SEGY QC job at a time to prevent from slowing down the system extensively

        :return: None
        """
        self.cursor.execute("SELECT * FROM tasks where status =?", ('queue',))
        queue_tasks = self.cursor.fetchone()
        if queue_tasks == None:
            self.logging.info("No tasks in queue at the moment")
        else:
            for a_task in queue_tasks:
                (id, command, type, drive, sysip, submittime, status, logpath, exe_time, finish_time, exception) = a_task
                if type == 'segy_qc':
                    if os.path.exists(os.path.join(os.getcwd(),'segy_qc_lock')): # prevent the execution of more than one segy qc at a time
                        self.logging.info("Holding Task id: " + id + " another SEGY QC task is running")
                    else:
                        self.logging.info("Now Submitting Task id: " + id + 'Command => ' + command)
                        os.system(command)
                        file_handler = open(os.path.join(os.getcwd(), 'segy_qc_lock'), 'w')
                        file_handler.close()
                        self.logging.info("SEGY QC lock created for execution of task id: " + id)
                        try:
                            self.cursor.execute("UPDATE tasks SET status = ? WHERE id=?",('submit',id))
                            self.logging.info('Task id: ' + id + " Changed from queue to submit")
                        except exception as e:
                            self.logging.error(e)
                else:
                    self.logging.info("Now Submitting Task id: " + id + 'Command => ' + command)
                    os.system(command)
                    try:
                        self.cursor.execute("UPDATE tasks SET status = ? WHERE id=?", ('submit', id))
                        self.logging.info('Task id: ' + id + " Changed from queue to submit")
                    except exception as e:
                        self.logging.error(e)

    def create_active_task_list_for_app(self):
        """
        Extract the list of active jobs at the present moment and dump them in form of a pickled dictionary

        { drive name : task details} ::: use segy_qc as the drive for segy qc tasks

        This file is sent to application by a run information sync service using sftp and used to populate logs

        :return: None
        """
        self.app_task_sync_lock(mode='create') # create the lock 1st and when this lock file exists the application will not SFTP the active tasks file
        self.cursor.execute("SELECT * FROM tasks WHERE status=?",('active',))
        active_tasks = self.cursor.fetchone()
        active_tasks_dict = {}
        if active_tasks ==None:
            self.logging.info("No active Tasks at the moment")
        else:
            for a_task in active_tasks:
                (id, command, type, drive, sysip, submittime, status, logpath, exe_time, finish_time, exception) = a_task
                key = status
                data = a_task
                active_tasks_dict.update({key:data})
            try:
                file_handler = open(os.path.join(os.getcwd(),'active_tasks'),'wb')
                pickle.dump(active_tasks_dict,file_handler)
                file_handler.close()
                self.logging.info("Active tasks picke file created")
            except Exception as e:
                self.logging.error(e)
        self.app_task_sync_lock(mode='remove')


    def app_task_sync_lock(self,mode):
        """
        Creates a file as a lock so that app does not sync the active tasks when the task execution daemaon is still writing to it

        :param mode: create ore remove the lock
        :return: none
        """
        if mode == 'create':
            try:
                file_handler = open(os.path.join(os.getcwd(), 'app_task_sync_lock'), 'w')
                file_handler.close()
                self.logging.info('App task sync lock created')
            except Exception as e:
                self.logging.error(e)
        elif mode == 'remove':
            try:
                os.remove(os.path.join(os.getcwd(), 'app_task_sync_lock'))
                self.logging.info('App task sync lock remvoed')
            except Exception as e:
                self.logging.error(e)

#-------------------------------------------------------------------------------
def main(db_file_path, mode):
    """
    Main function to control the execution of the deliverables_qc task execution daemon

    print the execution status to the screen

    write the detailed summary of execution and Exceptions in a log file

    wait 41 s and run again

    :param db_file_path: The full path of the database files that we need to connect with
    :param mode: 'normal' for standard execution, 'create_command' to create a test command
    :return: None

    """
    if mode == 'create_command':
        create_test_pickle()
    elif mode == 'normal':
        print "Creating log file ....."
        log_path = create_log_file(db_file_path)
        print 'Log path: ' + log_path
        print 'Done  ........'
        task_execution_service = Task_execution_service(log_path = log_path, database_path = db_file_path)
        while task_execution_service.database_connection:
            "Add all new commands supplied by the application to the database"
            print time.strftime('%a, %d %b %Y %H:%M:%S') + " : Exec => Add new commands to Database"
            task_execution_service.add_new_commands_to_database()
            print time.strftime('%a, %d %b %Y %H:%M:%S') + " : Exec => Sync Job status"
            task_execution_service.submitted_job_status_sync()
            print time.strftime('%a, %d %b %Y %H:%M:%S') + " : Exec => Create Active tasks for Application"
            task_execution_service.create_active_task_list_for_app()
            print time.strftime('%a, %d %b %Y %H:%M:%S') + " : Exec => Submit jobs from queue"
            task_execution_service.submit_new_jobs()
            print time.strftime('%a, %d %b %Y %H:%M:%S') + " : Waiting 41 sec before Next cycle"
            time.sleep(41)

    
def create_log_file(db_file_path):
    """    Create the log log file in the current directory
    :param db_file_path:
    :return:
    """
    log_dir = os.path.join(os.getcwd(),'Task_execution_daemon_logs')
    try:                  
        os.stat(log_dir)
    except:
        os.mkdir(log_dir)

    log_name = time.strftime("%Y%m%d-%H%M%S") + '.log'
    log_path = os.path.join(log_dir,log_name)
    file_handler = open(log_path,'wb')
    file_handler.write('Autogenerated log file created on : ' + time.strftime('%a, %d %b %Y %H:%M:%S') + '\n')
    file_handler.write('Database file : ' + db_file_path + '\n')
    file_handler.write('-'*80 + '\n')
    file_handler.close()
    return log_path


#-------------------------------------------------------------------------------

def create_test_pickle():
    type = 'SEGD'
    cmd = 'I am a test command ' # This needs to be replaced by a shell command later
    drive = 'dst0'
    sysip = '10.11.1.192'
    stime = '123456'
    status = 'queue'
    log_path = 'abcdmln;kn;'
    data_to_pickle = (cmd, type, drive, sysip, stime, log_path,status,)
    cmd_pickle_path = os.path.join(os.getcwd(), 'from_app','test_pickle4.cmd')
    file_handler = open(cmd_pickle_path, 'wb')
    pickle.dump(data_to_pickle, file_handler)
    file_handler.close()

if __name__ == '__main__':
    #main(db_file_path=os.path.join(os.getcwd(),'task_database.db'),mode='normal')
    main(db_file_path= sys.argv[1], mode=sys.argv[2])
    
