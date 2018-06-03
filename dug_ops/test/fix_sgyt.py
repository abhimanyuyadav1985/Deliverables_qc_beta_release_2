import os
import shutil
prefix = 'user_'

for a_file in os.listdir(os.getcwd()):
    if len(a_file.split('.')) == 2:
        if a_file.split('.')[1] == 'sgyt':
            source_path = os.path.join(os.getcwd(),a_file)
            new_f_name = prefix+a_file
            dest_path = os.path.join(os.getcwd(),new_f_name)
            print "copying : " + a_file
            shutil.copy(source_path,dest_path)