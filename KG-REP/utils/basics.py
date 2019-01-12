import os
import sys
import json
import pickle


def to_string(my_list, separator=' '):
    str_of_list = ''
    for i in my_list:
        str_of_list += str(str(i) + separator)
    max_len_str = len(str_of_list) - len(separator)
    return str_of_list[0:max_len_str]


def store_arguments(temp_path, *argv):
    ct = 0
    for arg in argv:
        ct += 1
        var_name = 'v' + str(ct)
        print var_name + ' = ' + str(arg)
        save_2_pickle(arg, os.path.join(temp_path, var_name + '.pickle'))


def pick_arguments(temp_path):
    print 'Entering pick_arguments from path - ' + temp_path
    arg_list = list()
    for ct in range(1, 100, 1):
        fn = os.path.join(temp_path, 'v' + str(ct) + '.pickle')
        if not os.path.isfile(fn):
            break
        print 'next file=' + fn
        obj = load_pickle_file(fn)
        arg_list.append(obj)
    print 'Exiting - pick_arguments() - number of args returned = ' + str(len(arg_list)) + '\n'
    return arg_list


def to_string_dict(my_dict, separator=','):
    str_of_list = ''
    for nk in my_dict.keys():
        str_of_list += separator + str(nk) + '=' + str(my_dict[nk])
    x=len(separator)
    return str_of_list[x:]


def print_status(msg, ct, print_at):
    att = '...........................................'
    if (ct % print_at) == 0:
        print format(ct, ",d") + ' ' + msg + att + '\r',
        sys.stdout.flush()


def load_json_file(path_file):
    print 'Starting to load JSON File - ' + path_file
    if not os.path.isfile(path_file):
        raise ValueError('No Such file - ' + path_file)
    ct, str_json,  = 0, ''
    with open(path_file) as f:
        content = f.readlines()
    for next_line in content:
        ct += 1
        str_json += next_line
        msg = 'load_json_file - ' + '     -->'
        print_status(msg, ct, 10)
    my_data_obj = json.loads(str_json)
    return my_data_obj


def save_json_to_file(data, path_file, rollover=False):
    if rollover:
        opf = open_file(path_file)
    else:
        opf = open(path_file, 'w')
    opf.write(json.dumps(data, indent=4))
    opf.close()


def get_line_count(path_file):
    ct = 0
    with open(path_file) as f:
        content = f.readlines()
    for next_line in content:
        ct += 1
    return ct


def convert_list_2_dict(list_obj, key):
    if list_obj is None:
        return None
    my_dict = dict()
    for next_item in list_obj:
        my_dict[next_item[key]] = next_item
    return my_dict


def save_2_pickle(data, path_file):
    pickle.dump(data, open(path_file, "wb"))


def load_pickle_file(path_file):
    return pickle.load(open(path_file, "rb"))


def ignore_exception(IgnoreException=Exception, DefaultVal=None):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    """
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal
        return _dec
    return dec


def open_file(path_file):
    p, f, e = get_extension(path_file)
    ct = 0
    while os.path.isfile(path_file):
        ct += 1
        path_file = os.path.join(p, f + '_' + str(ct) + e)
        print path_file
    return open(path_file, 'w')


def get_extension(path_file):
    f_name = os.path.basename(path_file)
    p = os.path.dirname(path_file)
    f = os.path.splitext(f_name)[0]
    e = os.path.splitext(f_name)[1]
    return p, f, e


def sort_map(my_map, isDescending=True, top_k=0):
    if len(my_map.keys()) > 1000:
        print '\nWARNING: Large Map being sorted....................................' + str(len(my_map.keys()))
    sorted_list_of_keys = list()
    ct = 0
    for rel, cos_simi in sorted(my_map.iteritems(), key=lambda (k, v): (v, k), reverse=isDescending):
        ct += 1
        sorted_list_of_keys.append(rel)
        if top_k !=0 and ct > top_k:
            break
    return sorted_list_of_keys


def filter_map(my_map, isDescending=True, top_k=0):
    if len(my_map.keys()) > 4000:
        print '\nWARNING: Large Map being filtered....................................' + str(len(my_map.keys()))
    filtered_map = dict()
    ct = 0
    for rel, cos_simi in sorted(my_map.iteritems(), key=lambda (k, v): (v, k), reverse=isDescending):
        ct += 1
        filtered_map[rel] = cos_simi
        if top_k != 0 and ct > top_k:
            break
    return filtered_map


if __name__ == '__main__':
    op_file = open_file('/home/puneet/MyWorkspaces/bkp/a/a.txt')
    op_file.write('aa')
    op_file.close()
    a = dict()
    a['x'] = 10
    a['y'] = 1
    a['z'] = 8
    print sort_map(a, True)
