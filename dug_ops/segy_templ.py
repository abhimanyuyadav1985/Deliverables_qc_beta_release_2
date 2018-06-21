import os,sys
from configuration import *
import datetime

def create_sgyt(deliverable,sequence,IL_range,XL_range,reel):
    # 1 Fetch master SGYt from database and create a file from it in the temp directory
    master_file_name = 'Master_' + str(deliverable.id)+"_" + deliverable.name + '.sgyt'
    deliverable_sgyt_master_from_db = deliverable.sgyt.decode('base64')
    master_file_path = os.path.join(os.getcwd(),'temp',master_file_name)
    try:
        os.remove(master_file_path)
        print "Deleting the exsting master file.."
    except:
        pass
    fout_master = open(master_file_path,'wb')
    for line in deliverable_sgyt_master_from_db.split('\n'):
        print >> fout_master,line
    fout_master.close()

    # 2 now create the file for the sequence wise SGYT
    seq_file_name = str(sequence.seq) + "_" + str(deliverable.id)+"_" + deliverable.name + '.sgyt'
    seq_file_path = os.path.join(os.getcwd(),'temp',seq_file_name)

    try:
        os.remove(seq_file_path)
        print "Deleting the exsting sequence file.."
    except:
        pass

    fout = open(seq_file_path, 'wb')

    # 3 Mechanics to create the sequence wise SGYT using replacements frrom database and user inputs
    with open(master_file_path, "rb") as f:
        b = f.read()
        a = b.split('\n')
        ebcdic = a[0][14:].decode('base64')
        lb = len(a[0][14:])
        l = len(ebcdic)
        #modify the items in quotations to change substitutions
        ebcdic = ebcdic.replace('ABCDEFGHIJKLMNOP', sequence.real_line_name)
        ebcdic = ebcdic.replace('FGSP-LGSP', '{0:04d}-{1:04d}'.format(int(sequence.fgsp), int(sequence.lgsp)))
        if len(str(sequence.seq)) == 3:
            ebcdic = ebcdic.replace('SSS', '{0:03d}'.format(int(sequence.seq)))
        elif len(str(sequence.seq)) == 4:
            ebcdic = ebcdic.replace('SSSS', '{0:04d}'.format(int(sequence.seq)))
        elif len(str(sequence.seq)) == 5:
            ebcdic = ebcdic.replace('SSSSS', '{0:05d}'.format(int(sequence.seq)))

        ebcdic = ebcdic.replace('DD-MM-YYYY', str(sequence.start_data))
        ebcdic = ebcdic.replace('FFID-LFID','{0:04d}-{1:04d}'.format(int(sequence.fg_ffid), int(sequence.lg_ffid)))
        # ebcdic = ebcdic.replace('mnXL-mxXL', '{:>4}-{:>4}'.format(XL_range[0], XL_range[1]))
        # ebcdic = ebcdic.replace('mnIL-mxIL', '{:>4}-{:>4}'.format(IL_range[0], IL_range[1]))
        ebcdic = ebcdic.replace('mnXL-mxXL','{0:04d}-{1:04d}'.format(int(XL_range[0]),int(XL_range[1]))) # Now prints a 5 digit IL and XL numbers with zero in begining to fill gaps
        ebcdic = ebcdic.replace('mnIL-mxIL','{0:04d}-{1:04d}'.format(int(IL_range[0]),int(IL_range[1])))
        ebcdic = ebcdic.replace('reel','{0:04d}'.format(int(reel))) # Now defaults to a 4 digit tape number putting zero in the begiing if needed
        # Now time to extract the current date ( This can be used with the 3D stack)
        d = datetime.date.today()
        date_tuple_obj = d.timetuple()
        ebcdic = ebcdic.replace('mm','{0:02d}'.format(int(date_tuple_obj.tm_mon)))
        ebcdic = ebcdic.replace('dd','{0:02d}'.format(int(date_tuple_obj.tm_mday)))
        ebcdic = ebcdic.replace('yyyy','{0:04d}'.format(int(date_tuple_obj.tm_year)))
        #---------------------------------------------------------------------------------
        for s in xrange(0,l,80):
            print ebcdic[s:s+80]

        a[0] = 'ebcdic_header ' + ebcdic.encode('base64')
        a[0] = a[0].replace('\n', '')
        lino_done = False
        for s in a:
            if 'lino' in s:
                if lino_done:
                    pass
                else:
                    s = '    lino {0:s} '.format(sequence.preplot_name[-len(str(sequence.preplot_name)):])
                    lino_done = True
            #if 'reno' in s:
                #s = '    reno ' + str(int(reel))

            print >> fout, s

    fout.close()

    return seq_file_name

def create_3D_sgyt(deliverable,IL_range,XL_range,reel):
    # 1 Fetch master SGYt from database and create a file from it in the temp directory
    master_file_name = 'Master_' + str(deliverable.id)+"_" + deliverable.name + '.sgyt'
    deliverable_sgyt_master_from_db = deliverable.sgyt.decode('base64')
    master_file_path = os.path.join(os.getcwd(),'temp',master_file_name)
    try:
        os.remove(master_file_path)
        print "Deleting the exsting master file.."
    except:
        pass
    fout_master = open(master_file_path,'wb')
    for line in deliverable_sgyt_master_from_db.split('\n'):
        print >> fout_master,line
    fout_master.close()

    # 2 now create the file for the sequence wise SGYT
    file_name = str(deliverable.id)+"_" + deliverable.name + '.sgyt'
    file_path = os.path.join(os.getcwd(),'temp',file_name)

    try:
        os.remove(file_path)
        print "Deleting the exsting sequence file.."
    except:
        pass

    fout = open(file_path, 'wb')

    # 3 Mechanics to create the sequence wise SGYT using replacements frrom database and user inputs
    with open(master_file_path, "rb") as f:
        b = f.read()
        a = b.split('\n')
        ebcdic = a[0][14:].decode('base64')
        lb = len(a[0][14:])
        l = len(ebcdic)
        #modify the items in quotations to change substitutions
        # ebcdic = ebcdic.replace('mnXL-mxXL', '{:>4}-{:>4}'.format(XL_range[0], XL_range[1]))
        # ebcdic = ebcdic.replace('mnIL-mxIL', '{:>4}-{:>4}'.format(IL_range[0], IL_range[1]))
        ebcdic = ebcdic.replace('mnXL-mxXL','{0:04d}-{1:04d}'.format(int(XL_range[0]),int(XL_range[1]))) # Now prints a 5 digit IL and XL numbers with zero in begining to fill gaps
        ebcdic = ebcdic.replace('mnIL-mxIL','{0:04d}-{1:04d}'.format(int(IL_range[0]),int(IL_range[1])))
        ebcdic = ebcdic.replace('reel','{0:04d}'.format(int(reel))) # Now defaults to a 4 digit tape number putting zero in the begiing if needed
        # Now time to extract the current date ( This can be used with the 3D stack)
        d = datetime.date.today()
        date_tuple_obj = d.timetuple()
        ebcdic = ebcdic.replace('mm','{0:02d}'.format(int(date_tuple_obj.tm_mon)))
        ebcdic = ebcdic.replace('dd','{0:02d}'.format(int(date_tuple_obj.tm_mday)))
        ebcdic = ebcdic.replace('yyyy','{0:04d}'.format(int(date_tuple_obj.tm_year)))
        #---------------------------------------------------------------------------------
        for s in xrange(0,l,80):
            print ebcdic[s:s+80]

        a[0] = 'ebcdic_header ' + ebcdic.encode('base64')
        a[0] = a[0].replace('\n', '')

        for s in a:
            if 'reno' in s:
                #s = '    reno ' + str(int(reel))
                pass

            print >> fout, s

    fout.close()

    return file_name

def encode_file(file):
    file_handler = open(file, 'rb')
    file_text = file_handler.read()
    encoded_string = file_text.encode('base64')
    return encoded_string


def decode_string(coded_string):
    decoded_text = coded_string.decode('base64')
    return decoded_text


def return_ebcdic_from_sgyt(decoded_string):
    a = decoded_string.split('\n')
    ebcdic = a[0][14:].decode('base64')
    return ebcdic


if __name__ == '__main__':
    print "This is main"

if __name__ == '__main__':
    print "This is main"


    
    
