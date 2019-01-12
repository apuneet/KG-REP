"""
This program is used to create a file in following format

Rel-Det-QID, Question-Pattern, Set of Valid Relation Sequences

"""

import os
import sys


data_dir = '/data/Work-Homes/LOD_HOME/KBQA_RE_data/KBQA_RE_data-master/webqsp_relations/'


def check_input_arguments():
    if len(sys.argv) < 1:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <epocs> \n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' 10\n')
        sys.exit(1)


def load_relations(fn='/data/Work-Homes/LOD_HOME/KBQA_RE_data/KBQA_RE_data-master/webqsp_relations/relations.txt'):
    my_relations = list()
    my_relations.append('none')
    with open(fn) as f:
        content = f.readlines()
    for next_line in content:
        my_relations.append(next_line.replace('\n', ''))
    return my_relations


def read_data(fn, my_relations, id_prefix, my_ques_list):
    ct = 0
    path_fn = os.path.join(data_dir, fn)
    with open(path_fn) as f:
        content = f.readlines()
    for next_line in content:
        my_ques_dict = dict()
        toks = next_line.split('\t')
        my_ques_dict['id'] = id_prefix + str(ct)
        my_ques_dict['ques'] = toks[2].replace('\n', '')
        rels = toks[0]
        rel_string = ''
        for next_rel in rels.split():
            next_rel_int = int(next_rel)
            rel_string += my_relations[next_rel_int] + ';'
        my_ques_dict['gt-rel-seq'] = rel_string
        ct += 1
        my_ques_list.append(my_ques_dict)
    return my_ques_list


def print_kbqa_all(my_ques_list):
    op_file = open(os.path.join(data_dir, 'my_questions.txt'), 'w')
    for next_question in my_ques_list:
        op_file.write(next_question['id'] + '\t' + next_question['ques'] + '\t' + next_question['gt-rel-seq'] + '\n')
    op_file.close()


def get_kbqa_data():
    my_relations = load_relations()
    my_ques_list = read_data('WebQSP.RE.train.with_boundary.withpool.dlnlp.txt', my_relations, 'KBQA-WQSP-Trn-', list())
    my_ques_list = read_data('WebQSP.RE.test.with_boundary.withpool.dlnlp.txt', my_relations,
                             'KBQA-WQSP-Tst-', my_ques_list)
    return my_ques_list


if __name__ == "__main__":
    check_input_arguments()




