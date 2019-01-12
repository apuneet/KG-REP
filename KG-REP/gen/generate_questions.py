"""
It takes
"""
import os
import sys
import json
from utils import basics as bas_utils

dp_home, dp_name = '', 'fb15k'
node_map_file, rel_map_file, question_set_path, path_pair_folder = '', '', '', ''
node_map_fn, rel_map_fn, template_fn = 'node-map-fb15k.txt', 'rel-map-fb15k.txt', 'set-3.csv'

working_dir = 'wip-data/query_prep/'


def check_input_arguments():
    if len(sys.argv) < 2:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <template_file_name(without path)>\n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' set-1.csv\n')
        sys.exit(1)
    global dp_home, node_map_file, rel_map_file, template_file, question_set_path, template_fn, path_pair_folder
    template_fn = sys.argv[1]
    dp_home = os.path.join(os.environ['WORK_DIR'], dp_name)
    node_map_file = os.path.join(dp_home, 'kg', node_map_fn)
    rel_map_file = os.path.join(dp_home, 'kg', rel_map_fn)
    template_file = os.path.join(dp_home, working_dir, 'templates', template_fn)
    path_pair_folder = os.path.join(dp_home, working_dir, '3_path_pair_data')
    set_name = os.path.splitext(template_fn)[0]
    question_set_path = os.path.join(dp_home, working_dir, 'ready_question_sets', set_name)
    os.path.isdir(question_set_path) or os.mkdir(question_set_path)
    print 'node_map_file=', node_map_file
    print 'rel_map_file=', rel_map_file
    print 'template_file=', template_file
    print 'question_set_path=', question_set_path
    print 'path_pair_folder=', path_pair_folder
    print '========================================================='


def load_map(filename):
    my_map = {}
    with open(filename) as f:
        content = f.readlines()
    for next_line in content:
        tokens = next_line.split()
        my_map[tokens[0]] = tokens[1]
    return my_map


def load_templates():
    fn_map, ct = {}, 0
    with open(template_file) as f:
        content = f.readlines()
    for next_line in content:
        if next_line.find('<e1>') < 0:
            print 'Skipping following line : \n' + next_line
            continue
        if next_line.find('<e2>') < 0:
            continue
        tokens = next_line.replace('\n', '').split(';')
        if len(tokens) < 5 or int(tokens[1]) < 3:
            continue
        file_name = tokens[0]
        q1 = tokens[3]
        q2 = tokens[4]
        q3 = tokens[4]
        my_list = list()
        if q1.find('<e1>') < 0 or q1.find('<e2>') < 0 or q2.find('<e1>') < 0 or q2.find('<e2>') < 0 \
                or q3.find('<e1>') < 0 or q3.find('<e2>') < 0:
            print 'Skipping Question for ' + file_name
            continue
        ct += 1
        my_list.append(q1)
        my_list.append(q2)
        my_list.append(q3)
        fn_map[file_name] = my_list
    print 'Number of Templates Loaded = ' + str(ct)
    return fn_map


def generate_questions(fn_map, node_map, rel_map, strategy=2, top_k=10):
    l1, l2, l3, qct = top_k, top_k*2, top_k*3, 0
    gt_train, gt_valid, gt_test = list(), list(), list()
    for fn in fn_map.keys():
        file_name_path, ct = os.path.join(path_pair_folder, fn), 0
        lc = bas_utils.get_line_count(file_name_path)
        part_ct = lc/3
        if part_ct < 10:
            l1, l2, l3 = part_ct, part_ct*2, part_ct*3
        else:
            l1, l2, l3 = top_k, top_k * 2, top_k * 3
        with open(file_name_path) as f:
            content = f.readlines()
        for next_line in content:
            tokens = next_line.split(',')
            if len(tokens) < 5:
                continue
            ct += 1
            if ct > l3:
                break
            qo1, qo2, qo3 = prepare_gt(fn_map[fn][0], fn_map[fn][1], fn_map[fn][2], node_map[tokens[0]], tokens[0],
                                       node_map[tokens[5]], tokens[5], rel_map[tokens[1]], tokens[1],
                                       rel_map[tokens[3]], tokens[3], rel_map[tokens[6]], tokens[6],
                                       rel_map[tokens[8]], tokens[8], fn)
            if strategy == 1:
                gt_train, gt_valid, gt_test, qct = get_same_q_in_three_sets(qo1, qo2, qo3, ct, qct, l1, l2, l3,
                                                                            gt_train, gt_valid, gt_test)
            else:
                gt_train, gt_valid, gt_test, qct = get_exclusive_data(qo1, qo2, qo3, ct, qct, l1, l2, l3,
                                                                      gt_train, gt_valid, gt_test)
    return gt_train, gt_valid, gt_test


def get_exclusive_data(qo1, qo2, qo3, ct, qct, l1, l2, l3, trn_set, val_set, tst_set):
    qct += 1
    if ct <= l1:
        qo1['qid'] = 'Trn-S2-' + str(qct)
        trn_set.append(qo1)
    if l1 < ct <= l2:
        qo2['qid'] = 'Val-S2-' + str(qct)
        val_set.append(qo2)
    if l2 < ct <= l3:
        qo3['qid'] = 'Tst-S2-' + str(qct)
        tst_set.append(qo3)
    return trn_set, val_set, tst_set, qct


def get_same_q_in_three_sets(qo1, qo2, qo3, ct, qct, l1, l2, l3, trn_set, val_set, tst_set):
    qid_prefix = ''
    if ct <= l1:
        trn_set.append(qo1)
        trn_set.append(qo2)
        trn_set.append(qo3)
        qid_prefix = 'Trn-S1-'
    if l1 < ct <= l2:
        val_set.append(qo1)
        val_set.append(qo2)
        val_set.append(qo3)
        qid_prefix = 'Val-S1-'
    if l2 < ct <= l3:
        tst_set.append(qo1)
        tst_set.append(qo2)
        tst_set.append(qo3)
        qid_prefix = 'Tst-S1-'
    qct += 1
    qo1['qid'] = qid_prefix + str(qct)
    qct += 1
    qo2['qid'] = qid_prefix + str(qct)
    qct += 1
    qo3['qid'] = qid_prefix + str(qct)
    return trn_set, val_set, tst_set, qct


def prepare_gt(q1, q2, q3, e1, en1, e2, en2, r1, rn1, r2, rn2, r3, rn3, r4, rn4, template_name):
    q1a = q1.lower().replace('<e1>', e1)
    q2a = q2.lower().replace('<e1>', e1)
    q3a = q3.lower().replace('<e1>', e1)
    q1b = q1a.replace('<e2>', e2)
    q2b = q2a.replace('<e2>', e2)
    q3b = q3a.replace('<e2>', e2)
    gt1 = q1b + ';' + e1 + ';' + e2 + ';' + r1 + ';' + r2 + ';' + r3 + ';' + r4
    gt2 = q2b + ';' + e1 + ';' + e2 + ';' + r1 + ';' + r2 + ';' + r3 + ';' + r4
    gt3 = q3b + ';' + e1 + ';' + e2 + ';' + r1 + ';' + r2 + ';' + r3 + ';' + r4
    qo1 = get_q_obj(q1b, e1, en1, e2, en2, r1, rn1, r2, rn2, r3, rn3, r4, rn4, template_name, 1)
    qo2 = get_q_obj(q2b, e1, en1, e2, en2, r1, rn1, r2, rn2, r3, rn3, r4, rn4, template_name, 2)
    qo3 = get_q_obj(q3b, e1, en1, e2, en2, r1, rn1, r2, rn2, r3, rn3, r4, rn4, template_name, 3)
    return qo1, qo2, qo3


def get_q_obj(q, e1, en1, e2, en2, r1, rn1, r2, rn2, r3, rn3, r4, rn4, template_name, variation_no):
    qo = dict()
    qo['qm'] = q.replace(',', ' ')
    qo['fq'] = q
    qo['src_ent_id'] = [e1, e2]
    qo['src_ent'] = [en1, en2]
    qo['rid_seq'] = [r1, r2, r3, r4]
    qo['rel_seq'] = [rn1, rn2, rn3, rn4]
    qo['template_name'] = template_name
    qo['q_variation_no'] = variation_no
    qo['is_ready'] = 3
    return qo


def print_questions(question_list, prefix):
    output_file_name = os.path.join(question_set_path, prefix + '.json')
    op_file = open(output_file_name, 'w')
    for i in question_list:
        op_file.write(i + '\n')
    op_file.close()
    print('Created file - ', output_file_name)


def print_json(output_path_file, json_obj, is_map=False):
    json_list = list()
    if is_map:
        for k in json_obj.keys():
            json_list.append(json_obj[k])
    else:
        json_list = json_obj
    op_file = open(output_path_file, 'w')
    op_file.write(json.dumps(json_list, indent=4, sort_keys=True))
    op_file.close()


def main():
    node_map = load_map(node_map_file)
    rel_map = load_map(rel_map_file)
    fn_map = load_templates()
    gt_train, gt_valid, gt_test = generate_questions(fn_map, node_map, rel_map)
    print 'len(gt_train) = ' + str(len(gt_train))
    print 'len(gt_valid) = ' + str(len(gt_valid))
    print 'len(gt_test) = ' + str(len(gt_test))
    print_json(os.path.join(question_set_path, 'kgt_trn.json'), gt_train)
    print_json(os.path.join(question_set_path, 'kgt_val.json'), gt_valid)
    print_json(os.path.join(question_set_path, 'kgt_tst.json'), gt_test)


if __name__ == '__main__':
    check_input_arguments()
    main()
