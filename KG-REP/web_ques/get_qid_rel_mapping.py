"""
1.
"""

import os
import utils.basics as bas_utils

data_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/'
trn_file = 'WebQSP.train.json'
tst_file = 'WebQSP.test.json'

input_folder = ''
#output_file = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/create-subgraph/docs/qid-rel-map-trn.txt'
output_file = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/create-subgraph/docs/qid-rel-map-tst.txt'

# Copy the output file to /data/Work-Homes/LOD_HOME/WebQSP/anal


def get_qid_rel_map(web_qsp_obj):
    qid_rel_map = list()
    for nxt_obj in web_qsp_obj['Questions']:
        qid = nxt_obj['QuestionId']
        chain = nxt_obj['Parses'][0]['InferentialChain']
        if chain is None or len(chain) < 1:
            continue
        for r in chain:
            l = qid + ',' + r
            qid_rel_map.append(l)
    my_str = bas_utils.to_string(qid_rel_map, '\n')
    op_file = open(output_file, 'w')
    op_file.write(my_str + '\n')
    op_file.close()
    print '\nOutput stored in file - ' + output_file



if __name__ == '__main__':
    #trn_obj = bas_utils.load_json_file(os.path.join(data_folder, trn_file))
    trn_obj = bas_utils.load_json_file(os.path.join(data_folder, tst_file))
    get_qid_rel_map(trn_obj)
