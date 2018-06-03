header_dict = {
    'project': 'G1',
    'client_project_id':'G2',
    'set_no':'G3',
    'date':'G4'
}

column_dict = {
    'tape_no':'A',
    'line_name':'B',
    'f_ffid':'C',
    'l_ffid':'D',
    'fsp':'E',
    'lsp': 'F',
    'shipment_no':'G',
    'box_no':'H'

}

start_row = 8

omit_row_list = [51,101,151,201,251,301,351,401,451,501,551,601,651,701] # can add more to make it longer in case we have so many tapes