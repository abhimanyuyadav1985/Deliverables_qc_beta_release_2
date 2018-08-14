#--------The relative positions to min and mx header extraction from the last column -1
trc_header_parser_dict = {
    'Min': 3,
    'Max': 2
}

#-------------Add identifiers here ----------------------------------------
EBCDIC_identifier = 'EBCDIC HEADER='
bin_identifier = 'BINARY FILE HEADER='
trc_identifier = 'TRACE HEADER='
log_end = '----------------'
trace_count_identifier = 'TRACES PROCESSED'
file_size_identifier = 'DATA PROCESSED'

#-------------This is used to print labels and some help files later
type_name_dict = {
    'SEQG' : 'Sequence Wise gathers',
    '2DSTK' : '2D stacked data',
    'NFH' : 'Near Field hydrophone data',
    '2DVEL' : '2D velocity data',
    '3DSTK' : '3D stacked data',
    '3DGATH' : '3D gathers',
    '3DVEL' : '3D velocity data'
}
#---------------------Type wise dictionary ------------------------------------
SEQG_dict = {
    'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 16,
        'trc': 18,
    },
    'ebcdic':{
        'SAIL LINE': ['ebcdic_line_name', 1,['line_name']],
        'EBCDIC Reel no':['ebcdic_reel_no', 2,['sgyt_reel_no']],
        'FGSP':['ebcdic_fgsp',3,['sgyt_fgsp']],
        'LGSP': ['ebcdic_lgsp',4,['sgyt_lgsp']],
        'FGFFID': ['ebcdic_min_ffid',5,['sgyt_min_ffid']],
        'LGFFID': ['ebcdic_max_ffid',6,['sgyt_max_ffid']],
        'MIN IL': ['ebcdic_min_il',7,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',8,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',9,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',10,['sgyt_max_xl']]
    },
    'trc':{
        'Min FFID': ['trc_min_ffid',1,['Original field record number', 'Min']],
        'Max FFID': ['trc_max_ffid',2,['Original field record number', 'Max']],
        'Min SP': ['trc_min_sp',3,['Energy source point', 'Min']],
        'Max SP': ['trc_max_sp',4,['Energy source point', 'Max']],
        'EDIT FLAG Min' : ['trc_min_trc_flag',5,['Trace identification code','Min']],
        'EDIT FLAG Max': ['trc_max_trc_flag',6,['Trace identification code', 'Max']],
        'Min Water depth' :['trc_min_wb',7,['Water depth at source','Min']],
        'Min IL':['trc_min_il',8,['3D inline number','Min']],
        'Max IL':['trc_max_il',9,['3D inline number','Max']],
        'Min XL':['trc_min_xl',10,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',11,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',12,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',13,['Ensemble coordinate - Y','Min']],
        'Sail Line': ['trc_line_name',14,['Numerical sail line number','Min']],
        'Min Src x': ['trc_src_min_x',15,['Source coordinate - X (scalar #2)','Min']],
        'Min Src y': ['trc_src_min_y',16,['Source coordinate - Y (scalar #2)','Min']],
        'Min Rec x': ['trc_rec_min_x',17,['Receiver group coordinate - X (scalar #2)','Min']],
        'Min Rec y':['trc_rec_min_y',18,['Receiver group coordinate - Y (scalar #2)','Min']]
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy','trc_rec_min_x','trc_rec_min_y','trc_src_min_x','trc_src_min_y'],
    #'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','ffid_match_flag','sp_match_flag','il_match_flag','xl_match_flag']
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','ffid_match_flag','sp_match_flag']

}
#-----------------------------------------------------
STK2D_dict = {
    'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 16,
        'trc': 18,
    },
    'ebcdic':{
        'SAIL LINE': ['ebcdic_line_name', 1,['line_name']],
        'EBCDIC Reel no':['ebcdic_reel_no', 2,['sgyt_reel_no']],
        'FGSP':['ebcdic_fgsp',3,['sgyt_fgsp']],
        'LGSP': ['ebcdic_lgsp',4,['sgyt_lgsp']],
        'FGFFID': ['ebcdic_min_ffid',5,['sgyt_min_ffid']],
        'LGFFID': ['ebcdic_max_ffid',6,['sgyt_max_ffid']],
        'MIN IL': ['ebcdic_min_il',7,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',8,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',9,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',10,['sgyt_max_xl']]
    },
    'trc':{
        'Min FFID': ['trc_min_ffid',1,['Original field record number', 'Min']],
        'Max FFID': ['trc_max_ffid',2,['Original field record number', 'Max']],
        'Min SP': ['trc_min_sp',3,['Energy source point', 'Min']],
        'Max SP': ['trc_max_sp',4,['Energy source point', 'Max']],
        'EDIT FLAG Min' : ['trc_min_trc_flag',5,['Trace identification code','Min']],
        'EDIT FLAG Max': ['trc_max_trc_flag',6,['Trace identification code', 'Max']],
        'Min Water depth' :['trc_min_wb',7,['Water depth at source','Min']],
        'Min IL':['trc_min_il',8,['3D inline number','Min']],
        'Max IL':['trc_max_il',9,['3D inline number','Max']],
        'Min XL':['trc_min_xl',10,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',11,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',12,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',13,['Ensemble coordinate - Y','Min']],
        'Sail Line': ['trc_line_name',14,['Numerical sail line number','Min']],
        'Min Src x': ['trc_src_min_x',15,['Source coordinate - X (scalar #2)','Min']],
        'Min Src y': ['trc_src_min_y',16,['Source coordinate - Y (scalar #2)','Min']],
        'Min Rec x': ['trc_rec_min_x',17,['Receiver group coordinate - X (scalar #2)','Min']],
        'Min Rec y':['trc_rec_min_y',18,['Receiver group coordinate - Y (scalar #2)','Min']]
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy','trc_rec_min_x','trc_rec_min_y','trc_src_min_x','trc_src_min_y'],
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','ffid_match_flag','sp_match_flag','il_match_flag','xl_match_flag']

}
#-----------------------------------------------------
NFH_dict = {
    'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 16,
        'trc': 18,
    },
    'ebcdic':{
        'SAIL LINE': ['ebcdic_line_name', 1,['line_name']],
        'EBCDIC Reel no':['ebcdic_reel_no', 2,['sgyt_reel_no']],
        'FGSP':['ebcdic_fgsp',3,['sgyt_fgsp']],
        'LGSP': ['ebcdic_lgsp',4,['sgyt_lgsp']],
        'FGFFID': ['ebcdic_min_ffid',5,['sgyt_min_ffid']],
        'LGFFID': ['ebcdic_max_ffid',6,['sgyt_max_ffid']],
        'MIN IL': ['ebcdic_min_il',7,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',8,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',9,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',10,['sgyt_max_xl']]
    },
    'trc':{
        'Min FFID': ['trc_min_ffid',1,['Original field record number', 'Min']],
        'Max FFID': ['trc_max_ffid',2,['Original field record number', 'Max']],
        'Min SP': ['trc_min_sp',3,['Energy source point', 'Min']],
        'Max SP': ['trc_max_sp',4,['Energy source point', 'Max']],
        'EDIT FLAG Min' : ['trc_min_trc_flag',5,['Trace identification code','Min']],
        'EDIT FLAG Max': ['trc_max_trc_flag',6,['Trace identification code', 'Max']],
        'Min Water depth' :['trc_min_wb',7,['Water depth at source','Min']],
        'Min IL':['trc_min_il',8,['3D inline number','Min']],
        'Max IL':['trc_max_il',9,['3D inline number','Max']],
        'Min XL':['trc_min_xl',10,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',11,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',12,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',13,['Ensemble coordinate - Y','Min']],
        'Sail Line': ['trc_line_name',14,['Numerical sail line number','Min']],
        'Min Src x': ['trc_src_min_x',15,['Source coordinate - X (scalar #2)','Min']],
        'Min Src y': ['trc_src_min_y',16,['Source coordinate - Y (scalar #2)','Min']],
        'Min Rec x': ['trc_rec_min_x',17,['Receiver group coordinate - X (scalar #2)','Min']],
        'Min Rec y':['trc_rec_min_y',18,['Receiver group coordinate - Y (scalar #2)','Min']]
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy','trc_rec_min_x','trc_rec_min_y','trc_src_min_x','trc_src_min_y'],
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','ffid_match_flag','sp_match_flag','il_match_flag','xl_match_flag']

}
#-----------------------------------------------------
VEL2D_dict = {
    'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 16,
        'trc': 18,
    },
    'ebcdic':{
        'SAIL LINE': ['ebcdic_line_name', 1,['line_name']],
        'EBCDIC Reel no':['ebcdic_reel_no', 2,['sgyt_reel_no']],
        'FGSP':['ebcdic_fgsp',3,['sgyt_fgsp']],
        'LGSP': ['ebcdic_lgsp',4,['sgyt_lgsp']],
        'FGFFID': ['ebcdic_min_ffid',5,['sgyt_min_ffid']],
        'LGFFID': ['ebcdic_max_ffid',6,['sgyt_max_ffid']],
        'MIN IL': ['ebcdic_min_il',7,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',8,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',9,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',10,['sgyt_max_xl']]
    },
    'trc':{
        'Min FFID': ['trc_min_ffid',1,['Original field record number', 'Min']],
        'Max FFID': ['trc_max_ffid',2,['Original field record number', 'Max']],
        'Min SP': ['trc_min_sp',3,['Energy source point', 'Min']],
        'Max SP': ['trc_max_sp',4,['Energy source point', 'Max']],
        'EDIT FLAG Min' : ['trc_min_trc_flag',5,['Trace identification code','Min']],
        'EDIT FLAG Max': ['trc_max_trc_flag',6,['Trace identification code', 'Max']],
        'Min Water depth' :['trc_min_wb',7,['Water depth at source','Min']],
        'Min IL':['trc_min_il',8,['3D inline number','Min']],
        'Max IL':['trc_max_il',9,['3D inline number','Max']],
        'Min XL':['trc_min_xl',10,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',11,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',12,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',13,['Ensemble coordinate - Y','Min']],
        'Sail Line': ['trc_line_name',14,['Numerical sail line number','Min']],
        'Min Src x': ['trc_src_min_x',15,['Source coordinate - X (scalar #2)','Min']],
        'Min Src y': ['trc_src_min_y',16,['Source coordinate - Y (scalar #2)','Min']],
        'Min Rec x': ['trc_rec_min_x',17,['Receiver group coordinate - X (scalar #2)','Min']],
        'Min Rec y':['trc_rec_min_y',18,['Receiver group coordinate - Y (scalar #2)','Min']]
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy','trc_rec_min_x','trc_rec_min_y','trc_src_min_x','trc_src_min_y'],
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','ffid_match_flag','sp_match_flag','il_match_flag','xl_match_flag']

}
#-----------------------------------------------------
STK3D_dict = {
    'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 11,
        'trc': 13,
    },
    'ebcdic':{
        'EBCDIC Reel no':['ebcdic_reel_no', 1,['sgyt_reel_no']],
        'MIN IL': ['ebcdic_min_il',2,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',3,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',4,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',5,['sgyt_max_xl']]
    },
    'trc':{
        'Min Water depth' :['trc_min_wb',1,['Water depth at source','Min']],
        'Min IL':['trc_min_il',2,['3D inline number','Min']],
        'Max IL':['trc_max_il',3,['3D inline number','Max']],
        'Min XL':['trc_min_xl',4,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',5,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',6,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',7,['Ensemble coordinate - Y','Min']],
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy'],
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','il_match_flag','xl_match_flag']

}
#-----------------------------------------------------
GATH3D_dict = {
    'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 11,
        'trc': 13,
    },
    'ebcdic':{
        'EBCDIC Reel no':['ebcdic_reel_no', 1,['sgyt_reel_no']],
        'MIN IL': ['ebcdic_min_il',2,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',3,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',4,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',5,['sgyt_max_xl']]
    },
    'trc':{
        'Min Water depth' :['trc_min_wb',7,['Water depth at source','Min']],
        'Min IL':['trc_min_il',8,['3D inline number','Min']],
        'Max IL':['trc_max_il',9,['3D inline number','Max']],
        'Min XL':['trc_min_xl',10,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',11,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',12,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',13,['Ensemble coordinate - Y','Min']],
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy'],
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','il_match_flag','xl_match_flag']

}
#-----------------------------------------------------
VEL3D_dict = {
        'ordered_key_list':['ebcdic','bin','trc'],
    'label_start_dict': {
        'ebcdic':5,
        'bin': 11,
        'trc': 13,
    },
    'ebcdic':{
        'EBCDIC Reel no':['ebcdic_reel_no', 1,['sgyt_reel_no']],
        'MIN IL': ['ebcdic_min_il',2,['sgyt_min_il']],
        'MAX IL': ['ebcdic_max_il',3,['sgyt_max_il']],
        'MIN XL' : ['ebcdic_min_xl',4,['sgyt_min_xl']],
        'MAX XL': ['ebcdic_max_xl',5,['sgyt_max_xl']]
    },
    'trc':{
        'Min Water depth' :['trc_min_wb',7,['Water depth at source','Min']],
        'Min IL':['trc_min_il',8,['3D inline number','Min']],
        'Max IL':['trc_max_il',9,['3D inline number','Max']],
        'Min XL':['trc_min_xl',10,['3D crossline number','Min']],
        'Max XL':['trc_max_xl',11,['3D crossline number','Max']],
        'Min CDP x':['trc_min_cdpx',12,['Ensemble coordinate - X','Min']],
        'Min CDP y':['trc_min_cdpy',13,['Ensemble coordinate - Y','Min']],
    },
    'bin':{
        'Bin Reel No':['bin_reel_no',1,['Reel number']]

    },
    'coordinate_flag_list':['trc_min_cdpx','trc_min_cdpy'],
    'flag_list':['sgyt_imp_exp_match_flag','trc_coordinate_zero_flag','wb_zero_flag','trc_type_flag','il_match_flag','xl_match_flag']

}
#--------------------------------Type wise name to Dictionary translator------------------------------------------------
type_dict = {
    'SEQG' : SEQG_dict,
    '2DSTK': STK2D_dict,
    'NFH' : NFH_dict,
    '2DVEL': VEL2D_dict,
    '3DSTK': STK3D_dict,
    '3DGATH' : GATH3D_dict,
    '3DVEL' : VEL3D_dict
}
#-----------------------------------------------------------------------------------------------------------------------
#this is used to put name to the items in the flag in GUI mode
flag_name_dict = {
    'sgyt_imp_exp_match_flag' : 'SGYT import export match flag',
    'trc_coordinate_zero_flag' : 'Trace coordinate non zero flag',
    'wb_zero_flag' : 'Water depth at source non zero flag',
    'trc_type_flag' : 'Trace types are not same flag',
    'ffid_match_flag' : 'FFID range (EBCDIC and Trace) match flag',
    'sp_match_flag' : 'SP range (EBCDIC and Trace) match flag',
    'il_match_flag' : 'IL range (EBCDIC and Trace) match flag',
    'xl_match_flag' : 'XL range (EBCDIC and Trace) match flag'
}