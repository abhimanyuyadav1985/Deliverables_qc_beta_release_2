import sys, os

def main():
    file_path = str(sys.argv[1])
    string_status  = "successful"
    string_error = 'UNSUCCESSFUL'
    string_finish = 'End'
    if string_finish in open(file_path,'rb').read():
        finish_status = 1
        if string_status in open(file_path,'rb').read():
            qc_status =  1
        else:
            qc_status = 0
    else:
        if string_error in open(file_path,'rb').read():
            finish_status = 1
            qc_status = 0
        else:
            finish_status = 0
            qc_status = 0
    print str(finish_status) + str(qc_status)

if __name__ == '__main__':
    main()