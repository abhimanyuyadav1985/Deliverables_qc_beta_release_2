from PyQt4 import QtGui,QtCore
from general_functions.general_functions import create_central_labels

class SEGY_QC_Form(QtGui.QWidget):

    def __init__(self,parent):
        super(SEGY_QC_Form, self).__init__()
        #parent
        self.parent = parent


        #grid
        self.grid = QtGui.QGridLayout()
        self.setWindowTitle("SEGY QC Input form")


        # labels

        self.grid.addWidget(create_central_labels('SEGY QC Input'),0,0,1,3)
        self.grid.addWidget(create_central_labels('Select Deliverable'),1,0)
        self.grid.addWidget(create_central_labels('Select line'),2,0)



        # pushbuttons


        self.pb_execute = QtGui.QPushButton('Run')
        self.grid.addWidget(self.pb_execute,3,2)
        self.pb_execute.clicked.connect(self.execute)


        # combo boxes


        self.combo_deliverable = QtGui.QComboBox()
        self.combo_deliverable.setObjectName("Deliverable")
        self.grid.addWidget(self.combo_deliverable,1,1)
        self.combo_deliverable.addItems(self.parent.form_definition_for_SEGY_QC())
        self.combo_deliverable.setCurrentIndex(-1)
        self.combo_deliverable.blockSignals(False)
        self.combo_deliverable.currentIndexChanged.connect(self.deliverable_selected)



        self.combo_line = QtGui.QComboBox()
        self.combo_line.setObjectName("File name")
        self.grid.addWidget(self.combo_line,2,1)
        self.combo_line.blockSignals(False)
        self.combo_line.currentIndexChanged.connect(self.line_selected)



        self.setLayout(self.grid)



    def deliverable_selected(self):
        deliverable = str( self.combo_deliverable.currentText())
        print "Deliverable is set to: " + deliverable
        self.parent.Deliverable = self.parent.disp_name_dict[deliverable]
        self.parent.dir_service.set_deliverable(self.parent.Deliverable)
        self.combo_line.clear()
        self.combo_line.addItems(self.parent.form_definition_for_SEGY_QC_file())
        self.combo_line.setCurrentIndex(-1)


    def line_selected(self):
        if int(self.combo_line.currentIndex()) == -1:
            pass
        else:
            line_name = str(self.combo_line.currentText())
            print "Line name is set to: " + line_name


    def execute(self):

        self.combo_list = [
            self.combo_deliverable,
            self.combo_line,
        ]
        combo_entry_check = True
        for a_combo in self.combo_list:
            if a_combo.currentIndex() == -1:
                combo_entry_check = False
                print str(a_combo.objectName()) + " : Is blank aborting"

        if combo_entry_check == True:
            deliverable = str(self.combo_deliverable.currentText())
            line_name = str(self.combo_line.currentText())
            self.parent.Deliverable = self.parent.disp_name_dict[deliverable]
            if self.parent.Deliverable.bin_def_status and self.parent.Deliverable.trc_def_status:
                # now the deliverable is set, time to set the dir service to the deliverable
                self.parent.dir_service.set_deliverable(self.parent.Deliverable)
                # return the list of SEGY files for the deliverable in the large files+ deliverable dir
                self.parent.segy_qc_from_form(line_name)
                self.close()
            else:
                print "The bin.def and trc.def files for the deliberable are not defined !!!"














