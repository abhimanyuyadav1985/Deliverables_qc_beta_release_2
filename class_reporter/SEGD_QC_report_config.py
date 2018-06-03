header_dict = {
    'project': 'G1',
    'client_project_id':'G2',
    'set_no':'G3',
    'date':'G4',
    'shipment_no':'G5'
}

column_dict = {
    'tape_no':'A',
    'line_name':'B',
    'f_ffid':'C',
    'l_ffid':'D',
    'missing':'E',
    'number_files':'F',
    'qc_status':'G',
    'date_time_str':'H'
}

start_row = 8

omit_row_list = [51,101,151,201,251,301,351,401,451,501,551,601,651,701] # can add more to make it longer in case we have so many tapes