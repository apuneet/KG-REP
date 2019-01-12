import os
import glob
import utils.basics as bas_utils


data_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/'
trn_file = 'WebQSP.train.json'
tst_file = 'WebQSP.test.json'

core_graph_folder='/data/Work-Homes/LOD_HOME/FB_SEMPRE/create-subgraph-3/core-graph-only/'
output_file = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data-3/final_qid_sid_mapping.txt'


def create_qid_sid_map(qmap):
    op_file = open(output_file, 'w')
    for fn in glob.glob(core_graph_folder + '*.ans'):
        qid = os.path.basename(fn)[:-8]
        next_obj = qmap[qid]
        first_rel = 'fb:' + next_obj['Parses'][0]['InferentialChain'][0]
        topic_ent = ''
        with open(fn) as f:
            content = f.readlines()
        for next_line in content:
            toks = next_line.split()
            if len(toks) < 3:
                continue
            if toks[1] == first_rel and topic_ent == '':
                topic_ent = toks[0]
            if toks[1] == first_rel and topic_ent != toks[0]:
                print "================........... ERROR ........============="
                print 'More than one subject for the same topic entity' + qid
        op_file.write(qid + ',' + topic_ent + '\n')
    op_file.close()


def list_2_map(list1, list2):
    my_dict = dict()
    for i in list1:
        qid = i['QuestionId']
        my_dict[qid] = i
    for i in list2:
        qid = i['QuestionId']
        my_dict[qid] = i
    return my_dict


if __name__ == "__main__":
    trn_obj = bas_utils.load_json_file(os.path.join(data_folder, trn_file))
    print '\n - Training JSON Loaded'
    tst_obj = bas_utils.load_json_file(os.path.join(data_folder, tst_file))
    print '\n - Test JSON Loaded'
    merged_map = list_2_map(trn_obj['Questions'], tst_obj['Questions'])
    print '\n - Merged the two Maps'
    create_qid_sid_map(merged_map)



