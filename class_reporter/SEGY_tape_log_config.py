header_dict = {
    'project': 'H1',
    'client_project_id': 'H2',
    'set_no': 'H3',
    'date': 'H4'
}

column_dict = {
    'reel_no': 'A',
    'media_label': 'B',
    'line_name': 'C',
    'sgyt_min_ffid': 'D',
    'sgyt_max_ffid': 'E',
    'sgyt_fgsp': 'F',
    'sgyt_lgsp': 'G',
    'sgyt_min_il': 'H',
    'sgyt_max_il': 'I',
    'sgyt_min_xl': 'J',
    'sgyt_max_xl': 'K',
    'shipment_no': 'L',
    'box_no': 'M',
    'use_tag': 'N'

}

column_dict_3D = {}
start_row = 8

o_row_list = [34]
for i in range(1, 101):
    o_row_list.append(o_row_list[i - 1] + 33)
    if i == 100:
        omit_row_list = o_row_list
