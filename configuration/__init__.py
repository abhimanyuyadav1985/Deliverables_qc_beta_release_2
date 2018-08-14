"""


Module: configuration
==========================

Author : Abhimanyu Yadav

This module is used for defining hard settings to be used by the SW application

Hard settings definition
-------------------------
use_locations  (list)  Site location and it is used to decipher site specific settings like IP addresses




This needs further work
"""
import os
from unipath import Path


import logging
from app_log import  stream_formatter
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(stream_formatter)
console.setFormatter(formatter)
logger.addHandler(console)

#-------------------------------------------------------------------------------------
use_locations = ['Dubai','Nadia','Naila','Asima','Alima','Amani','Adira']
#--------------------------------------------------------------------------------------

deliverable_classes = ['SEGD','SEGY']
deliverable_type_list = ['SEQG','2DSTK','NFH','3DSTK','3DGATH','3DVEL','2DVEL']
# These are used to decide the GUI class applicable to a particular deliverable type
sequence_wise_SEGY = ['SEQG','2DSTK','NFH','2DVEL']
SEGY_3D = ['3DSTK','3DGATH','3DVEL']

valid_media_list = ['3592 JA','3592 JC','DVD','USB','3592 JA .tar','3592 JC .tar','3592 JA multiple','3592 JC multiple']

SEGY_write_to_media_table_list = [('SEQG','3592 JA'),('SEQG','3592 JC'),('SEQG','3592 JA multiple'),('SEQG','3592 JC multiple')] # this is used to decide if for a particular deliverable when SEGY write is approved should we create an entry in media label as well or not

multiple_per_tape_list = ['3592 JA multiple', '3592 JC multiple']

file_size_allowed_dict = {
    '3592 JA' : 491520,
    '3592 JC' : 4194304,
    '3592 JA multiple' : 491520,
    '3592 JC multiple' : 4194304

} # all the sizes are in mebibyte MiB

SEGY_tape_log_template_dict = {
    'SEQG': 'SEGY_Tape_log_sequence_wise.xlsx',
    '2DSTK': 'SEGY_Tape_log_sequence_wise.xlsx',
    'NFH': 'SEGY_Tape_log_sequence_wise.xlsx',
    '2DVEL': 'SEGY_Tape_log_sequence_wise.xlsx',
    '3DSTK' : 'SEGY_Tape_log_3D.xlsx',
    '3DGATH' : 'SEGY_Tape_log_3D.xlsx',
    '3DVEL' : 'SEGY_Tape_log_3D.xlsx',
} # this is used to decide which SEGY tape log template should be used


deliverables_dir= "deliverables"
deliverable_qc_subdirs_dict = {'SEGY':['write_log'],"SEGD":['logfile'], }
data_dirs_dict = {'SEGY':['masters','headers','sample'],'SEGD':["segd.segd"]}

large_file_root_dict = {'Dubai':'/node/dubai0193/large_files',
                        'Nadia':'/nadia/large_files',
                        'Naila':'/naila/large_files',
                        'Asima':'/asima/large_files',
                        'Adira':'/adira/large_files',
                        'Amani':'/amani/large_files',
                        'Alima':'/alima/large_files'}

#-------------------------------------------------------------------------
# Directories
media_path = "media"
Report_dir = "Reports"
Templates_dir = "Templates"
#Excel Templates
SEGD_QC_report_template = 'SEGD_QC.xlsx'
SEGD_Tape_log_template = 'SEGD_Tape_log.xlsx'
change_log_report_template = 'change_delete_log.xlsx'

#----Top window----------------
version = "_B_20180814.1"
config_check = False
default_use_env = ""
echo_mode = False

#----connection
conn_config_file = os.path.join("configuration",'Tape_QC_configuration.ini')
orca_schema_name = 'orca'
deliverables_qc_schema_name = 'deliverables_qc'


#Dictionary for resolving Tape server IP based on vessel name in the configuration file
Tape_server_dict = {'Dubai':'10.11.2.193','Nadia':"","Naila":"10.102.20.23","Asima":"10.105.20.23","Alima":"10.106.20.23","Amani":"10.107.20.23","Adira":"10.108.20.23"}

dubai_tape_drive_list = ['dst0','dst1']
vessel_tape_drive_list = ['dst0','dst1','dst2','dst3','dst4','dst5']

location_wise_tape_driver_dict = {'Dubai': dubai_tape_drive_list,
                                  "Nadia":vessel_tape_drive_list,
                                  "Naila":vessel_tape_drive_list,
                                  "Asima":vessel_tape_drive_list,
                                  'Alima':vessel_tape_drive_list,
                                  'Amani':vessel_tape_drive_list,
                                  "Adira":vessel_tape_drive_list}


#---------------------------------------------------------------------------
def get_segd_qc_script():
    orignal = 'segd_tape_QC.sh'
    file_path = os.path.join(os.getcwd(), 'manual_overrides', 'segd_qc')
    logger.info("Reading SEGD QC script from =>  " + file_path)
    if os.path.exists(file_path):
        try:
            file_handler = open(file_path,'rb')
            for a_line in file_handler.readlines():
                if 'SEGD_QC_SCRIPT' in a_line.rstrip():
                    logger.info("Using New: " + str(a_line.rstrip().split("=")[1]))
                    orignal =  str(a_line.rstrip().split("=")[1])
            return orignal
            file_handler.close()
        except Exception as error:
            logger.error(error)
            logger.info("Using default: segd_tape_QC.sh")
            return orignal
    else:
        logger.warning("Not found : " + file_path)
        return orignal


segd_qc_script = get_segd_qc_script()


def get_segy_write_script():
    orignal = 'segy_tape_write.sh'
    logger.info("Checking if SEGY write script is manually changed")
    try:
        file_path = os.path.join(os.getcwd(), 'manual_overrides', 'segy_w')
        file_handler = open(file_path, 'rb')

        for a_line in file_handler.readlines():
            if 'SEGY_W_SCRIPT' in a_line.rstrip():
                logger.info("Using New: " + str(a_line.rstrip().split("=")[1]))
                orignal =  str(a_line.rstrip().split("=")[1])
        return orignal
    except Exception as error:
        logger.error(error)
        logger.info("Using default: segy_tape_write.sh")
        return orignal


segy_write_script = get_segy_write_script()

#--------------------------------Use mode selection ----------------------
#use_mode = "Demo"
use_mode = 'Production'

config_check = False
if use_mode == "Demo":
    default_use_mode = False
elif use_mode == 'Production':
    default_use_mode = True
#-------------------------------------------------------------------------------------------