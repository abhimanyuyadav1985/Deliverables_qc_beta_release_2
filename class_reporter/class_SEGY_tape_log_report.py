from PyQt4 import QtCore
import datetime
from SEGY_tape_log_config import header_dict,column_dict,start_row,omit_row_list
from configuration import Templates_dir, Report_dir
import shutil
import win32com.client as win32
import os

class SEGY_tape_log_header(object):
    def __init__(self,proj_info_obj,set_no,shipment_no):
        self.project = proj_info_obj.project
        self.client_project_id = proj_info_obj.client_project_id
        self.no_of_sets = set_no
        self.shipment_no = shipment_no
        self.date = datetime.datetime.now().strftime ("%Y%m%d")


class SEGY_tape_log_report(QtCore.QObject):

    finished = QtCore.pyqtSignal()
    doingWork = QtCore.pyqtSignal(bool,str,str)


    def __init__(self,header,data,file_name,thread_name,template_name):
        super(SEGY_tape_log_report, self).__init__()

        self.header = header
        self.data = data
        self.file_name = file_name
        self.thread_name = thread_name
        self.template_name = template_name

    def run(self):


        src_path = os.path.join(os.getcwd(), Templates_dir,self.template_name)
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
            ws.Range(str(header_dict["date"])).Value = self.header.date

            row = start_row

            for obj in self.data:
                if str(obj.set_no) == str(set):
                    self.doingWork.emit(True,str("Adding Tape : " + obj.reel_no),self.thread_name)
                    if row in omit_row_list:
                        row = row +1

                    ws.Range(str(column_dict["reel_no"])+ str(row)).Value = obj.reel_no
                    ws.Range(str(column_dict["line_name"]) + str(row)).Value = obj.line_name
                    ws.Range(str(column_dict["sgyt_min_ffid"]) + str(row)).Value = obj.sgyt_min_ffid
                    ws.Range(str(column_dict["sgyt_max_ffid"]) + str(row)).Value = obj.sgyt_max_ffid
                    ws.Range(str(column_dict["sgyt_fgsp"]) + str(row)).Value = obj.sgyt_fgsp
                    ws.Range(str(column_dict["sgyt_lgsp"]) + str(row)).Value = obj.sgyt_lgsp
                    ws.Range(str(column_dict["shipment_no"]) + str(row)).Value = obj.shipment_no
                    ws.Range(str(column_dict["box_no"]) + str(row)).Value = obj.box_no
                    ws.Range(str(column_dict["sgyt_min_il"]) + str(row)).Value = obj.sgyt_min_il
                    ws.Range(str(column_dict["sgyt_max_il"]) + str(row)).Value = obj.sgyt_max_il
                    ws.Range(str(column_dict["sgyt_min_xl"]) + str(row)).Value = obj.sgyt_min_xl
                    ws.Range(str(column_dict["sgyt_max_xl"]) + str(row)).Value = obj.sgyt_max_xl
                    ws.Range(str(column_dict["use_tag"]) + str(row)).Value = obj.use_tag
                    ws.Range(str(column_dict["media_label"]) + str(row)).Value = obj.media_label

                    row = row+1

        self.doingWork.emit(True,str("Now saving Excel : " + self.file_name),self.thread_name)
        wb.Save()
        excel.Application.Quit()
        self.doingWork.emit(False,"Done.....",self.thread_name)
        self.finished.emit()