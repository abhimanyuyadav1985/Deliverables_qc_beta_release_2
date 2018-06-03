from PyQt4 import QtCore
import datetime
from change_delete_log_config import column_dict,start_row
from configuration import Templates_dir, Report_dir, change_log_report_template
import shutil
import win32com.client as win32
import os

class change_log_report(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    doingWork = QtCore.pyqtSignal(bool,str,str)


    def __init__(self,data,file_name,thread_name):
        super(change_log_report, self).__init__()

        self.data = data
        self.file_name = file_name
        self.thread_name = thread_name

    def run(self):
        src_path = os.path.join(os.getcwd(), Templates_dir,change_log_report_template)
        dest_path = os.path.join(os.getcwd(),Report_dir,self.file_name)
        shutil.copy(src_path,dest_path)

        win32.pythoncom.CoInitialize()
        excel = win32.gencache.EnsureDispatch('Excel.Application')

        wb = excel.Workbooks.Open(dest_path)
        excel.Visible = False

        # now write to excel in a set wise manner
        sheet_list = ['change','delete']
        for sheet_name in sheet_list:
            row = start_row
            ws = wb.Worksheets(sheet_name)
            for obj in self.data:
                if str(obj.type_entry) == sheet_name:
                    self.doingWork.emit(True,str("Adding obj : " + str(obj.id_cl)),self.thread_name)
                    ws.Range(str(column_dict["id_cl"])+ str(row)).Value = obj.id_cl
                    ws.Range(str(column_dict["type_entry"]) + str(row)).Value = obj.type_entry
                    ws.Range(str(column_dict["location"]) + str(row)).Value = obj.location
                    ws.Range(str(column_dict["details"]) + str(row)).Value = obj.details
                    ws.Range(str(column_dict["date"]) + str(row)).Value = obj.date
                    ws.Range(str(column_dict["user_name"]) + str(row)).Value = obj.user_name
                    row = row+1

        self.doingWork.emit(True,str("Now saving Excel : " + self.file_name),self.thread_name)
        wb.Save()
        excel.Application.Quit()
        self.doingWork.emit(False,"Done.....",self.thread_name)
        self.finished.emit()