from PyQt4 import QtCore

class db_pinger(object):
    def __init__(self,parent):
        self.parent = parent
        self.db_connection_obj = self.parent.db_connection_obj

        timer = QtCore.QTimer()
        timer.timeout.connect(self.ping_server)
        timer.start(2000)



    def ping_server(self):
        conn = self.db_connection_obj.db_engine.connect()
        cursor = conn.cursor()
        try:

            cursor.execute("SELECT 1")
        except:
            print "raising disconnect error"
        cursor.close()

