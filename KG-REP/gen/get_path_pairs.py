"""
This program ensures that the chosen pair of paths have no common relation, so that the finally there are four unique
relations involved in the tree.
"""

import os
import sys
from utils import basics as bas_utils

dp_home, dp_name, single_paths_folder, path_pair_data_folder = '', 'fb15k', '', ''
single_path_template_file_name = ''
working_dir = 'wip-data/query_prep'


def check_input_arguments():
    if len(sys.argv) < 2:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <Target-Type-Name>\n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' Actor\n')
        sys.exit(1)
    global dp_home, single_paths_folder, path_pair_data_folder, single_path_template_file_name
    dp_home = os.path.join(os.environ['WORK_DIR'], dp_name)
    single_paths_folder = os.path.join(dp_home, working_dir, '2_single_paths', sys.argv[1])
    path_pair_data_folder = os.path.join(dp_home, working_dir, '3_path_pair_data')
    single_path_template_file_name = os.path.join(dp_home, working_dir, '1_single_path_templates', sys.argv[1] + '.txt')
    print 'input - single_paths_folder=', single_paths_folder
    print 'output - path_pair_data_folder=', path_pair_data_folder
    print '==============================================================='


def load_file(fn):
    fp = os.path.join(single_paths_folder, fn)
    ct, my_list = 0, []
    with open(fp) as f:
        content = f.readlines()
    for line in content:
        ct += 1
        tokens = line.split(',')
        if len(tokens) < 6:
            print 'less than 6 tokens in line = ' + line
            continue
        my_d = dict()
        my_d['e1'] = tokens[0]
        my_d['r1'] = tokens[1]
        my_d['e2'] = tokens[2]
        my_d['r2'] = tokens[4]
        my_d['e3'] = tokens[5].replace('\n', '')
        my_list.append(my_d)
    return my_list


def print_questions(qs, new_file_path, rel_count=-1):
    print '\nstarted printing'
    op_file = open(new_file_path, 'w')
    ct = 0
    print 'len(qs) = ' + str(len(qs))
    for q in qs:
        next_q = ''
        ct += 1
        bas_utils.print_status('print_questions()', ct, 1)
        my_list = []
        for p in q:
            my_list.append(p['r1'])
            my_list.append(p['r2'])
            next_q = next_q + p['e1'] + ',' + p['r1'] + ',' + p['e2'] + ',' + p['r2'] + ',' + p['e3'] + ','
        if (rel_count > 0) and (len(set(my_list)) == rel_count):
            op_file.write(next_q + '\n')
        elif rel_count < 0:
            op_file.write(next_q + '\n')
        else:
            print next_q
            print '-----------'
            print my_list
            print '-----------'
            print set(my_list)
            print '================='
            raw_input("Press Enter to see more Examples...")
    op_file.close()
    print 'printing complete....'


def compare_files(f1, f2):
    print 'compare_files() - ' + f1 + ', ' + f2
    l1 = load_file(f1)
    l2 = load_file(f2)
    qs, ct = [], 0
    for i in l1:
        for j in l2:
            ct += 1
            bas_utils.print_status('compare_files()', ct, 1)
            if i['e3'] != j['e3']:
                continue
            q = list()
            q.append(i)
            q.append(j)
            qs.append(q)
    return qs


def check_if_rel_common(ct1, ct2):
    l1, l2, ct, is_common = '', '', 0, False
    with open(single_path_template_file_name) as f:
        content = f.readlines()
    for line in content:
        ct += 1
        if line.startswith('#'):
            continue
        if ct == ct1:
            l1 = line
        if ct == ct2:
            l2 = line
    toks1 = l1.split(',')
    toks2 = l2.split(',')
    my_list = list()
    my_list.append(toks1[3])
    my_list.append(toks1[4].replace('\n', ''))
    my_list.append(toks2[3])
    my_list.append(toks2[4].replace('\n', ''))
    if len(set(my_list)) != 4:
        is_common = True
    return is_common


def generate_path_pairs():
    print 'Generating questions for target = ' + single_paths_folder
    os.path.exists(path_pair_data_folder) or os.mkdir(path_pair_data_folder)
    file_list = os.listdir(single_paths_folder)
    i, ct = 0, 0
    for i in range(0, len(file_list)):
        for j in range(i, len(file_list)):
            if i == j:
                continue
            ct += 1
            print str(ct) + ') ' + file_list[i] + '===' + file_list[j]
            f1_ct = file_list[i].split('-')[0]
            f2_ct = file_list[j].split('-')[0]
            if check_if_rel_common(int(f1_ct), int(f2_ct)):
                print 'These paths meet sooner ...'
                continue
            qs = compare_files(file_list[i], file_list[j])
            op_file_path = os.path.join(path_pair_data_folder,
                                        os.path.basename(single_paths_folder) + '-' + f1_ct + '-' + f2_ct + '.csv')
            print_questions(qs, op_file_path, 4)


if __name__ == '__main__':
    check_input_arguments()
    generate_path_pairs()
