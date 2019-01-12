import os
import utils.basics as bas_utils

data_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/'
trn_file = 'WebQSP.train.json'
tst_file = 'WebQSP.test.json'

rel_file = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/no-rel-in-kg.txt'


def load_rel_file():
    rel_set = set()
    with open(rel_file) as f:
        content = f.readlines()
    for next_line in content:
        rel_set.add(next_line.replace('\n', ''))
    print 'load_rel_file() - size = ' + str(len(rel_set))
    return rel_set


def main(wqsp_obj, rels):
    for next_q in wqsp_obj:
        chain = next_q['Parses'][0]['InferentialChain']
        if chain is None:
            continue
        for r in chain:
            mr = 'fb:'+r
            if mr in rels:
                print next_q['QuestionId'] + ' - ' + str(len(chain))


if __name__ == '__main__':
    #trn_obj = bas_utils.load_json_file(os.path.join(data_folder, trn_file))
    trn_obj = bas_utils.load_json_file(os.path.join(data_folder, tst_file))
    print '\nWebQSP file loaded...'
    rel_set = load_rel_file()
    main(trn_obj['Questions'], rel_set)