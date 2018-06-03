from PyQt4 import QtCore
import datetime
from SEGD_QC_report_config import header_dict,column_dict,start_row,omit_row_list
from configuration import Templates_dir, Report_dir,SEGD_QC_report_template
import shutil
import win32com.client as win32
import os

class SEGD_QC_header(object):
    def __init__(self,proj_info_obj,set_no,shipment_no):
        self.project = proj_info_obj.project
        self.client_project_id = proj_info_obj.client_project_id
        self.no_of_sets = set_no
        self.shipment_no = shipment_no
        self.date = datetime.datetime.now().strftime ("%Y%m%d")


class SEGD_QC_report(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    doingWork = QtCore.pyqtSignal(bool,str,str)


    def __init__(self,header,data,file_name,thread_name):
        super(SEGD_QC_report, self).__init__()

        self.header = header
        self.data = data
        self.file_name = file_name
        self.thread_name = thread_name

    def run(self):


        src_path = os.path.join(os.getcwd(), Templates_dir,SEGD_QC_report_template)
        dest_path = os.path.join(os.getcwd(),Report_dir,self.file_name)
        shutil.copy(src_path,dest_path)

        win32.pythoncom.CoInitialize()
        excel = win32.gencache.EnsureDispatch('Excel.Application')

        wb = excel.Workbooks.Open(dest_path)
        excel.Visible = False
        ws = wb.Worksheets('Set_1') # This is the empty sheet that needs to be copied multiple times
        for set in range(2,int(self.header.no_of_sets)+1):
            ws_name = str("Set_" + str(set))
            print "Now creating a new WS .." + ws_name,
            ws.Copy(win32.pythoncom.Empty, wb.Sheets(wb.Sheets.Count))
            new_ws = wb.Sheets(wb.Sheets.Count)
            new_ws.Name = ws_name
            print "Done .... "

        # now write to excel in a set wise manner
        for set in range(1,int(self.header.no_of_sets) +1 ):
            self.doingWork.emit(True,str("Now working on Set: " + str(set)),self.thread_name)
            ws_name = str('Set_' + str(set))
            ws = wb.Worksheets(ws_name)
            #now print the header
            ws.Range(str(header_dict["project"])).Value = self.header.project
            ws.Range(str(header_dict["client_project_id"])).Value = self.header.client_project_id
            ws.Range(str(header_dict["set_no"])).Value = set
            ws.Range(str(header_dict["shipment_no"])).Value = self.header.shipment_no
            ws.Range(str(header_dict["date"])).Value = self.header.date

            row = start_row

            for obj in self.data:
                if str(obj.set_no) == str(set):
                    self.doingWork.emit(True,str("Adding Tape : " + obj.tape_no),self.thread_name)
                    if row in omit_row_list:
                        row = row +1

                    ws.Range(str(column_dict["tape_no"])+ str(row)).Value = obj.tape_no
                    ws.Range(str(column_dict["line_name"]) + str(row)).Value = obj.line_name
                    ws.Range(str(column_dict["f_ffid"]) + str(row)).Value = obj.f_ffid
                    ws.Range(str(column_dict["l_ffid"]) + str(row)).Value = obj.l_ffid
                    ws.Range(str(column_dict["missing"]) + str(row)).Value = obj.missing
                    ws.Range(str(column_dict["number_files"]) + str(row)).Value = obj.number_files
                    ws.Range(str(column_dict["qc_status"]) + str(row)).Value = obj.qc_status
                    ws.Range(str(column_dict["date_time_str"]) + str(row)).Value = obj.date_time_str

                    row = row+1

        self.doingWork.emit(True,str("Now saving Excel : " + self.file_name),self.thread_name)
        wb.Save()
        excel.Application.Quit()
        self.doingWork.emit(False,"Done.....",self.thread_name)
        self.finished.emit()