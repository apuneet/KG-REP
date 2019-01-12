"""
This takes <target_type>.txt, .e.g., Location.txt file as input.
This file should be present in the folder $DP_HOME/wip-data/query_prep/1_single_path_templates/

The Location.txt contains rows in following format
entity_type_name-1, entity_type_name-2, entity_type_name-3, relation-1, relation-2

1.  It creates directory named "target_type" in following path - $DP_HOME/wip-data/query_prep/2_single_paths
2.  Based on the inputs in terms of pair of relations, it will create many files in the above folder, with filenames
<ct>-<entity_type_name-1>-<entity_type_name-2>-<entity_type_name-3>, e.g., 1-Directed-by-Film-Person(Actor).txt
These files contain: s1, r2, o1, s2, r2, o2
Here, o1 and s2 should be equal.

"""
import os
import sys
import utils
from utils import basics as bas_utils

dp_home, dp_name, single_path_template_file_name, = '', 'fb15k', ''
el_file_name = 'fb15k.txt'
working_dir = 'wip-data/query_prep'


def check_input_arguments(spt_fn=None):
    if spt_fn is None and len(sys.argv) < 2:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <Single Path Template File Name>\n')
        sys.stderr.write('This file should lie in WORK_DIR/<data package name>/wip-data/query_prep/1_single_path_templates\n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' Actor.txt\n')
        sys.exit(1)
    global dp_home, single_path_template_file_name
    dp_home = os.path.join(os.environ['WORK_DIR'], dp_name)
    if spt_fn is None:
        spt_fn = sys.argv[1]
    single_path_template_file_name = os.path.join(dp_home, working_dir, '1_single_path_templates', spt_fn)
    print 'single_path_template_file_name=', single_path_template_file_name


def load_data():
    """
    It loads the rdf triple file in dictionary of following format
    rel_map: key=relation, value=in_map
    in_map: key='sub' or 'obj', value=list of subjects / objects of that relationship

    :param el_file_name:
    :return: rel_map
    """
    el_file_path = os.path.join(dp_home, 'kg', el_file_name)
    rel_map, ct = {}, 0
    with open(el_file_path) as f:
        content = f.readlines()
    for line in content:
        ct += 1
        tokens = line.split()
        if len(tokens) < 3:
            print 'less than 3 tokens in line = ' + line
            continue
        rel = tokens[1]
        in_map = {}
        sub_list, obj_list = [], []
        if len(rel_map) > 0:
            keys = rel_map.keys()
            if rel in keys:
                in_map = rel_map[rel]
                sub_list = in_map['sub']
                obj_list = in_map['obj']
        sub_list.append(tokens[0])
        obj_list.append(tokens[2])
        in_map['sub'] = sub_list
        in_map['obj'] = obj_list
        rel_map[rel] = in_map
        print_status(ct, 200000)
    print_status(ct, 1)
    return rel_map


def get_paths(l1, l2, l3, l4, r1, r2):
    """
    It takes an intersection of the list of objects of r1, and subjects of r2.
    whenever object of r1 and subject of r2 are equal, it appends a path in the path_list

    :param l1: List of subjects of r1 relationship
    :param l2: List of objects of r1 relationship
    :param l3: List of subjects of r2 relationship
    :param l4: List of objects of r2 relationship
    :param r1: first relationship
    :param r2: second relationship
    :return: path_list
    """
    max_ct1 = len(l2)
    max_ct2 = len(l3)
    print 'ct(' + r1 + ')=' + format(max_ct1, ',d') + ', ct(' + r2 + ')=' + format(max_ct2, ',d')
    path_list = []
    ct = 0
    for i in range(0, max_ct1, 1):
        for j in range(0, max_ct2, 1):
            ct += 1
            #print_status(ct, 1000000)
            bas_utils.print_status('get_paths()', ct, 1)
            if l2[i] == l3[j]:
                path_list.append(l1[i] + ',' + r1 + ',' + l2[i] + ',' + l3[j] + ',' + r2 + ',' + l4[j])
    return path_list


def get_paths_unq_ent(l1, l2, l3, l4, r1, r2, main_ct):
    """
    It takes an intersection of the list of objects of r1, and subjects of r2.
    whenever object of r1 and subject of r2 are equal, it appends a path in the path_list

    :param l1: List of subjects of r1 relationship
    :param l2: List of objects of r1 relationship
    :param l3: List of subjects of r2 relationship
    :param l4: List of objects of r2 relationship
    :param r1: first relationship
    :param r2: second relationship
    :return: path_list
    """
    entity_set = set()
    max_ct1 = len(l2)
    max_ct2 = len(l3)
    max_ct = max_ct1 * max_ct2
    path_list = []
    ct = 0
    for i in range(0, max_ct1, 1):
        for j in range(0, max_ct2, 1):
            ct += 1
            utils.basics.print_status('get_paths_unq_ent() Total - ' + str(max_ct) + ' -- ', ct, 1000000)
            if l2[i] == l3[j] and check_if_path_ok(entity_set, l1[i], l2[i], l4[j]):
                entity_set.add(l1[i])
                entity_set.add(l2[i])
                entity_set.add(l4[j])
                path_list.append(l1[i] + ',' + r1 + ',' + l2[i] + ',' + l3[j] + ',' + r2 + ',' + l4[j])
    if len(path_list) > 5:
        print 'ct(' + r1 + ')=' + format(max_ct1, ',d') + ', ct(' + r2 + ')=' + format(max_ct2, ',d') \
              + ', ct=' + str(main_ct) + ', size=' + str(len(path_list))
    return path_list


def check_if_path_ok(entity_set, e1, e2, e3):
    my_list = [e1, e2, e3]
    my_set = set(my_list)
    if len(my_set) == 3 and e1 not in entity_set and e2 not in entity_set and e3 not in entity_set:
        return True
    else:
        return False




def print_status(ct, print_at):
    if (ct % print_at) == 0:
        print format(ct, ",d")


def print_paths(path_list, new_file_path, min_size=0):
    """
    This function prints the path_list in new_file_path
    :param path_list:
    :param new_file_path:
    :return:
    """
    if len(path_list) > min_size:
        op_file = open(new_file_path, 'w')
        for i in path_list:
            op_file.write(i + '\n')
        op_file.close()


def get_path_for_file():
    rel_map = load_data()
    print 'Data from file fb15k.txt loaded ... number of relations = ' + str(format(len(rel_map), ',d'))
    target_type = os.path.splitext(os.path.basename(single_path_template_file_name))[0]
    target_single_path_folder = os.path.join(dp_home, working_dir, '2_single_paths', target_type)
    os.path.exists(target_single_path_folder) or os.mkdir(target_single_path_folder)
    ct = 0
    with open(single_path_template_file_name) as f:
        content = f.readlines()
    for line in content:
        print "\n\nWorking on - " + line
        if line.startswith('#'):
            continue
        ct += 1
        tokens = line.split(',')
        t4 = tokens[4].replace('\n', '')
        new_file_name = str(ct) + '-' + tokens[0] + '-' + tokens[1] + '-' + tokens[2] + '.txt'
        new_file_path = os.path.join(target_single_path_folder, new_file_name)
        in_map_1 = rel_map[tokens[3]]
        in_map_2 = rel_map[t4]
        print 'Started Working on - ' + new_file_path
        path_list = get_paths(in_map_1['sub'], in_map_1['obj'], in_map_2['sub'], in_map_2['obj'], tokens[3], t4)
        print_paths(path_list, new_file_path)
    print 'Output files in folder - ' + target_single_path_folder


if __name__ == '__main__':
    check_input_arguments()
    get_path_for_file()
