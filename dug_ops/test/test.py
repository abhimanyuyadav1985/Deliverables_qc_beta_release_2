import paramiko
import time
import cStringIO


def main():
    # transport = paramiko.Transport('10.108.20.23',22)
    # transport.connect(username='adira0152',password='polarcus')
    # chan = transport.open_session()
    # chan.get_pty()
    # chan.invoke_shell()
    # chan.send('segd_tape_QC.sh tape=/dev/dst1 disk=/adira/contracts/adi041717_exxon_Guyana_Kaieteur/deliverables/1_argus_merged_segd/segd.segd/4300A101 log=/adira/contracts/adi041717_exxon_Guyana_Kaieteur/deliverables/1_argus_merged_segd/set_2/logfile/4300A101-HA0362-set2.log firstdisk=3381 lastdisk=4910 > /dev/null  2>&1')
    # print "Now disowning"
    # chan.send('disown')
    #
    # chan.exec_command('mt -t /dev/dst0 status')
    #
    # while True:
    #     if chan.recv_ready():
    #         output = chan.recv(1024)
    #         print output
    #     else:
    #         time.sleep(0.5)
    #         if not (chan.recv_ready()):
    #             break

    # chan.close()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname='10.11.2.193',port = 22, username = 'dubai0193', password='polarcus')
    stdin, stdout , stderr = client.exec_command('ps -ef | grep SEGD_QC')

    for line in stdout.readlines():
        if "SEGD_QC_run_daemon.py" in line:
            print line.rstrip("\n")
            print "Task execution daemon is running .. "
























if __name__ == '__main__':
    main()