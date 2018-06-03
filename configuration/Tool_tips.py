main_menu_dict = {
    'configuration' : 'Set up a new DUG and Database connection, The connection setting are stored in the ~/configuration directory as a Tape_QC_configuration.ini file. \n '
                      'Please do not make manual changes to the file as this is a pickle object and the applicaiton may not interpret it correctly if changed manually !!!',
    'deliverables' : 'Create new deliverables, check deliverables summary or view an existing deliverable / edit the ones you have created before.',
    'tape_dashboard' : 'Launch the tape dashboard. The tape dashboard is a virtual console to perform standard tape operations like rewind, eject, status, SEGD tape QC or SEGY write.',
    'segd_tools' : 'A SEGD toolkit. Check SEGD QC summary, print SEGD Tape logs and QC reports etc to excel files.',
    'segy_tools' : 'A SEGY toolkit. Check SEGY QC and production status, create SGYT files for DUG Insight or perform SEGY QC. \n'
                   ' Print SEGY tape and QC logs to excel files. ',
    'usb_tools' : 'Create new USB labels or .tar tape labels and associate data with them \n'
                  'Check the exists USB labels for the project along with their content',
    'shipments' : 'Create new shipments, check the summary and content of existing shipments and print shipment paperwork',
    'refresh' : 'Load the existing configuration and run synchronization service once again for the application to update the db entries with the most recent status.',
    'home' : 'Exit the current widget and return to the home screen ie Project information',
    'quit' : 'Quit the application',
    'change_log' : 'Print all change and delete activities to an excel file',
    'bug_report' : 'Send a bug report or development request to the team!'
}

segd_tools_dict = {
    'general' :'This is the SEGD QC tool kit. \n'
               'Check SEGD QC summary, print tape logs and QC reports',
    'show_status' :'Show the status for SEGD tape QC',
    'survey_wide_qc' : 'Create Excel format report for survey wide SEGD QC',
    'survey_wide_tape' :'Create Excel format report for survey wide SEGD Tape logs',
    'shipment_qc' : 'This tool is not active in the current release but it will be active soon..',
    'shipment_tape' :'This tool is not active in the current release but it will be active soon..'
}

segd_status_dict = {
    'general' : 'This is the SEGD status summary. \n'
                'Linename : This is the line name from ORCA \n'
                'Tape no : This is the tape number for the line from ORCA \n'
                '\n'
                'Prod : Represents the production status for the line from ORCA \n'
                'Run : The Status for SEGD tape QC execution \n'
                'QC : SEGD Tape QC status, you ca press the button to check the log !!'

}

segy_tools_dict = {
    'general' :'This is the SEGY tool kit. \n'
               'Used to check the SEGY QC and production status for SEGY deliverables \n'
               'Create .sgyt files \n'
               'Perfom SEGY QC on files in disk \n'
               'Create Excel format SEGY QC and Tape logs',
    'status' :'Print the SEGY QC and production status for a single SEGY class deliverable',
    'survey_wide_qc' :'Print the survey wide SEGY QC report for a single deliverables in Excel format',
    'shipment_wise_qc' :'This Function is not available in the current release',
    '2d_sgyt' :'Create DUG .sgyt files for sequence wise deliverables using manual entries and subsitutions from ORCA \n'
               'The sgyt file will be transferred automatically to the DUG system',
    '3d_sgyt' :'Create DUG .sgyt files for sequence wise deliverables using manual entries \n'
               'The sgyt file will be transferred automatically to the DUG system',
    'segy_qc' : 'Perform SEGY QC on a single on disk SEGY file',
    'survey_wide_tape' :'Print survey wide tape logs for a single SEGY deliverable in excel format',
    'shipment_tape' :'This function is not available in the current release'
}

segy_status_dict = {
    'general' : 'This is the SEGY production and QC status widget. \n'
                'On the top you have the details for the selected deliverable \n'
                'You can check the .sgyt, bin.def and trc.def files for the deliverable from the deliverable details section at the top \n'
                '\n'
                'Below that you have the SEGY QC and production tabs. These tabs are configured differently based on the type of the selected deliverable \n'
                '\n'
                'SGYT : Tab shows the production and QC status for the SGYT templates from the master for the deliverable \n'
                '\n'
                'On disk : Tab shows the production and QC status for SEGY file on disk \n'
                '           Please be aware that the option to export the deliverable will only show when you have approved the sgyt file \n'
                '\n'
                'Write QC : Tab shows the production and QC status for SEGY tape \n'
                '           Please be aware that the option to write a file to tape will only appear once the on disk file QC has been approved'


}

segy_tabs_2d_dict = {
    'sgyt' : 'This is the tab for Production and QC status for DUG sgyt files for the deliverable master template \n'
             'Please make sure that all the .sgyt files are created through the application and not manually !!! \n'
             '\n'
             'Seq_no : The sequence number from ORCA \n'
             '\n'
             'Line name : The line name from ORCA \n'
             '\n'
             'SGYT export : The segy template export status \n'
             '\n'
             'SGYT reel_no : The reel number used to create the SGYT file \n'
             '\n'
             'Exported by : Name of the user who exported the template \n'
             '\n'
             'Date : Timestamp for sgyt export \n'
             '\n'
             'QC run status : View the sgyt file exported by the application to approve it \n'
             '\n'
             'Approve : Approve the sgyt file exported by the application \n'
             '\n'
             'Approval status : Approval status for the sgyt file exported by the application \n'
             '\n'
             'Approved by : Name of the user appoving the template \n'
             '\n'
             'Approval time stamp : Time stamp for approval time',
    'on_disk' :  'This is the tab for Production and QC status for SEGY files on disk \n'
             'Items will only appear here if the SGYT file approval status is true !!! \n'
                 'Please make sure to create a segy template user_~ in the same directory at the time of SEGY export \n'
                 'This will be compared against the SEGY template exported by the application to ensure there were no manual changes or other issues!!!\n'
             '\n'
             'Seq_no : The sequence number from ORCA \n'
             '\n'
             'Line name : The line name from ORCA \n'
             '\n'
             'SGYT QC : The sgyt QC status \n'
             '\n'
             'Export : click here to verify that SEGY file has been exported on disk \n'
                 'If you are in doubt over the SEGY file name and export location simply hover over the pushbutton to check the expected location \n'
             '\n'
             'Exported status : SEGY file on disk export status \n'
             '\n'
             'Exported by : The name of the user validating the SEGY on disk export \n'
             '\n'
             'Time stamp: The time stamp for the SEGY export \n'
             '\n'
             'Link : Click the button to view th ouput log from the SEGY on disk QC \n \n'
             'Header : Status for header extraction, Headers are extraction from the view QC log widget \n'
             '\n'
             'Approve : Approve the SEGY file on disk \n'
             '\n'
             'Approval status : Approval status for the SEGY file on disk \n'
             '\n'
             'Approved by : Name of the user appoving the SEGY on disk QC  \n'
             '\n'
             'Approval time stamp : Time stamp for approval time',
}

segy_tabs_3d_dict = {

}

configuration_tool_dict = {
    'configuration' : 'This is the configuration tool menu used to define the DUG and DB connection settings \n' \
                         'Vessel : The location for use \n' \
                         'Database host IP : 10.10x.1.38 , x is the vessel identifier \n' \
                         'Database host user : irdb \n' \
                         'Database host password :  rd****** \n' \
                         'Database Name : proj_xxxxxx \n' \
                         'Database user name : fgeo \n' \
                         'Database port: 5432 \n' \
                         'Database password : P******123 \n' \
                         'DUG WS IP : IP for the DUG workstation you are trying to connect to \n' \
                         'DUG user : username for workstation \n' \
                         'DUG password : p****s \n' \
                         'DUG project path : Path to the parent fodler that will have the Insight project and the deliverables directory\n' \
                         '\n' \
                         'Save config: Test the current configuration settings and save to a Tape_QC_configuration.ini file in ~/configuration folder \n' \
                         'Load config : choose the configuration file you want to use, one configuration file per project. the one is use will always be saved as \n' \
                         'Tape_QC_configuration.ini so best to save another copy in a separate location is you want to connect to different projects'
}

deliverables_dict = {
    'general' : 'This is the deliverables Summary widget. Showing all the deliverables in the database for the Project . \n'
                'It is used to create a new deliverable or check / edit and delete and existing deliverable \n \n'
                'Id : Deliverable id is created automatically at the time of initializing a deliverable \n \n'
                'Name : simply the deliverable name, for 3D deliverable the SEGY file exprted should have the same name as the deliverable \n'
                '       for the sequencewuse deliverable the SEGY file name should be the same as line name please do not add a sufix or prefix while exporting \n \n'
                'Class : SEGD for SEGD deliverables and SEGY for SEGY deliverables \n \n'
                'Type : The following the type abbreviations for SEGD or SEGY deliverables \n'
                '   SEQG : Sequence wise 2D gathers ie shots etc \n'
                '   2DSTK : Sequence wise 2D STK \n'
                '   NFH : Sequecne wise NFH data \n '
                '   3DGATH : 3D sorted gathers \n'
                '   3DVEL : 3D Velocity field \n'
                '   2DVEL : 2D velocity field \n'
                '\n'
                'Media : Media for delivery \n \n'
                'Copies: Number of sets for the deliverable \n',
    'add' : 'Add a new deliverable',
    'view' : 'View an existing deliverable ( only view cannot edit)',
    'edit' : 'Edit and existing deliverable (Requires a change log entry) ',
    'delete' : 'Delete an existing deliverable (Requires a change log entry)',
    'exit' : 'Return to the home screen'

}

single_deliverable_dict = {
    'general' : 'Create a new deliverable and associated directories on the DUG system and the necessary Db entries',
    'id' : 'Deliverable id is created automatically at the time of initializing a deliverable',
    'name' : 'simply the deliverable name, for 3D deliverable the SEGY file exprted should have the same name as the deliverable \n'
                'for the sequencewuse deliverable the SEGY file name should be the same as line name please do not add a sufix or prefix while exporting',
    'class_d' : 'SEGD for SEGD deliverables and SEGY for SEGY deliverables',
    'type' : 'The following the type abbreviations for SEGD or SEGY deliverables \n'
                '   SEQG : Sequence wise 2D gathers ie shots etc \n'
                '   2DSTK : Sequence wise 2D STK \n'
                '   NFH : Sequecne wise NFH data \n '
                '   3DGATH : 3D sorted gathers \n'
                '   3DVEL : 3D Velocity field \n'
                '   2DVEL : 2D velocity field \n',
    'media' : 'Media for delivery',
    'copies' :'Number of sets for the deliverable',
    'prod_version' : 'Version for approval of segy descriptor',
    'reel_prefix' : 'The two digit reel prefix for the deliverables, not important for SEGD',
    'sgyt' : 'The DUG insight format segy template file master',
    'bin_def' : 'The binary header descriptor in the format for segy header checking module',
    'trc_def' : 'The trace header descriptor in the format for segy header checking module'

}

tape_dashboard_dict = {
    'refresh' : "Update the status for all the tape drives",
    'rewind' :'Rewind a single tape drive',
    'eject' : 'Eject a single tape drive',
    'segd_qc' :'Perform SEGD QC on a single Tape',
    'segy_write' :'Perform SEGY Tape write',
    'exit' : 'Hide the tape dashboard console'

}



tool_tips_mapper_dict = {
    'main_menu' : main_menu_dict,
    'deliverables' : deliverables_dict,
    'segd_tools' : segd_tools_dict,
    'segy_tools' : segy_tools_dict,
    'configuration' : configuration_tool_dict,
    'single_deliverable' : single_deliverable_dict,
    'tape_dashboard' : tape_dashboard_dict,
    'segd_status' : segd_status_dict,
    'segy_status' : segy_status_dict,
    'segy_tabs_2d' : segy_tabs_2d_dict,


}