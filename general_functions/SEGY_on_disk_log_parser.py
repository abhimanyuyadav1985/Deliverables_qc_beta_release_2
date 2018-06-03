from configuration.SEGY_header_type_wise import *

def extract_from_log(log_data,type):
    interpreter_dict = type_dict[type]
    i = 0
    log_line_list = []
    for line in log_data.split('\n'):
        print line
        if bin_identifier in line.rstrip('\n'):
            bin_start = i+1
        if trc_identifier in line.rstrip('\n'):
            bin_end = i-1
            trc_start = i+1
        if log_end in line.rstrip('\n'):
            trc_end = i-1
        log_line_list.append(line.rstrip('\n'))
        if trace_count_identifier in line.rstrip('\n'):
            line_to_use = line.rstrip('\n')
            line_list = line_to_use.split()
            dict_entry = {'trace_count': line_list[len(line_list)-1]}
        if file_size_identifier in line.rstrip("\n"):
            line_to_use = line.rstrip("\n")
            line_list = line_to_use.split()
            dict_entry.update({'file_size' : line_list[len(line_list)-2]})
        i = i + 1
    binary_data = log_line_list[bin_start:bin_end]
    trc_data = log_line_list[trc_start:trc_end]
    trc_update_dict = trc_parser(trc_data,interpreter_dict)
    bin_update_dict =  bin_parser(binary_data,interpreter_dict,trc_update_dict)
    bin_update_dict.update(dict_entry)
    return bin_update_dict


def trc_parser(trc_data,interpreter_dict):
    trc_dict = {}
    dict_to_use = interpreter_dict['trc']
    for key in dict_to_use.keys():
        search_string = dict_to_use[key][2][0]
        offset_setting = trc_header_parser_dict[dict_to_use[key][2][1]]
        #print search_string
        for a_line in trc_data:
            if search_string in a_line:
                list_to_use =  a_line.split()
                list_index = len(list_to_use)-offset_setting -1
                data_for_dict = list_to_use[list_index]
                dict_to_update = {dict_to_use[key][0]:data_for_dict}
                trc_dict.update(dict_to_update)
    # for key in trc_dict.keys():
    #     print key +" : " + str(trc_dict[key])
    return trc_dict

def bin_parser(bin_data,interpreter_dict,bin_dict):
    dict_to_use = interpreter_dict['bin']
    for key in dict_to_use.keys():
        search_string = dict_to_use[key][2][0]
        #print search_string
        for a_line in bin_data:
            if search_string in a_line:
                list_to_use = a_line.split()
                data_for_dict = list_to_use[len(list_to_use)-1]
                dict_to_update = {dict_to_use[key][0]:data_for_dict}
                bin_dict.update(dict_to_update)

    # for key in bin_dict.keys():
    #     print key + " : " + str(bin_dict[key])
    return bin_dict
