import os
from time import strftime
from ftplib import FTP
remote_file = 'Deliverables_QC_v20170520.1.7z'
file_path = os.path.join(os.getcwd(),'test',remote_file)
remote_path = '/FROM_OFFICE'

def ftp_connect(remote_path):
    link = FTP(host = 'ftp.polarcus.com') #Keep low timeout
    link.login(passwd = 's7789b0', user = 'dxb_ftsupport')
    debug("%s - Connected to FTP" % strftime("%d-%m-%Y %H.%M"))
    link.cwd(remote_path)
    return link

downloaded = open(file_path, 'wb')

def debug(txt):
    print txt

link = ftp_connect(remote_path)
file_size = link.size(remote_file)

max_attempts = 5 #I dont want death loops.

while file_size != downloaded.tell():
    try:
        debug("%s while > try, run retrbinary\n" % strftime("%d-%m-%Y %H.%M"))
        if downloaded.tell() != 0:
            link.retrbinary('RETR ' + remote_file, downloaded.write, downloaded.tell())
        else:
            link.retrbinary('RETR ' + remote_file, downloaded.write)
    except Exception as myerror:
        if max_attempts != 0:
            debug("%s while > except, something going wrong: %s\n \tfile lenght is: %i > %i\n" %
                (strftime("%d-%m-%Y %H.%M"), myerror, file_size, downloaded.tell())
            )
            link = ftp_connect(remote_path)
            max_attempts -= 1
        else:
            break
