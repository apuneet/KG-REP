import os
import utils.basics as bas_utils


data_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/'
trn_file = 'WebQSP.train.mod.json'
tst_file = 'WebQSP.test.json'

literal_relations_file = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/literal-rels.txt'
data_relations_file = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/data-rels.txt'

output_file_no_chain = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/anal/trn-no-chain.txt'
#output_file_no_chain = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/anal/tst-no-chain.txt'


output_file_chain_not_in_KG = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/anal/trn-chain-not-in-KG.txt'
#output_file_chain_not_in_KG = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/anal/tst-chain-not-in-KG.txt'


def analyze_data(wqsp_obj):
    constraint_dict = dict()
    for next_q in wqsp_obj:
        #cct = len(next_q['Parses'][0]['Constraints'])
        cct = len(next_q['Parses'])
        if cct in constraint_dict.keys():
            freq = constraint_dict[cct]
        else:
            freq = 0
        freq += 1
        constraint_dict[cct] = freq
    print bas_utils.to_string_dict(constraint_dict)


def count_no_core_chain(wqsp_obj):
    print 'Entering count_no_core_chain() >>>>>>>>>>>>>>'
    total_quest, ct = 0, 0
    no_chain_qids = set()
    for next_q in wqsp_obj:
        total_quest += 1
        parse_with_chain, parase_ct = -1, -1
        for next_parse in next_q['Parses']:
            parase_ct += 1
            if next_parse['InferentialChain'] is None or len(next_parse['InferentialChain']) == 0:
                continue
            if parse_with_chain == -1:
                parse_with_chain = parase_ct
        if parse_with_chain == -1:
            no_chain_qids.add(next_q['QuestionId'])
        else:
            ct += 1
        if parse_with_chain > 0:
            print next_q['QuestionId'] + ' - parse containing chain = ' + str(parse_with_chain)
    print 'InferentialChain=' + str(ct) + '/' + str(total_quest) + ' - ' + str((total_quest-ct))
    print 'len(no_chain_qids)=' + str(len(no_chain_qids))
    my_str = bas_utils.to_string(no_chain_qids, '\n')
    op_file = open(output_file_no_chain, 'w')
    op_file.write(my_str + '\n')
    op_file.close()
    print 'Exiting count_no_core_chain() <<<<<<<<<<<<<<'
    return no_chain_qids



def count_no_topic_ent(wqsp_obj):
    total_quest, ct = 0, 0
    for next_q in wqsp_obj:
        total_quest += 1
        for next_parse in next_q['Parses']:
            if next_parse['TopicEntityMid'] is not None and len(next_parse['TopicEntityMid']) > 0:
                ct += 1
                break
    print 'TopicEntityMid=' + str(ct) + '/' + str(total_quest) + ' - ' + str((total_quest-ct))


def count_no_ans(wqsp_obj):
    total_quest, ct = 0, 0
    for next_q in wqsp_obj:
        is_found = False
        total_quest += 1
        for next_parse in next_q['Parses']:
            if next_parse['Answers'] is not None and len(next_parse['Answers']) > 0:
                ct += 1
                is_found = True
                break
        #if not is_found:
        #    print 'No Ans-->' + next_q['QuestionId']
    print 'Answers=' + str(ct) + '/' + str(total_quest) + ' - ' + str((total_quest-ct))


def load_relations(file_name, rel_set):
    with open(file_name) as f:
        content = f.readlines()
    for next_line in content:
        nl = next_line.replace('\n', '')
        rel_set.add(nl)
    return rel_set


def count_relations_in_KG(wqsp_obj, no_chain_qids):
    print 'Entering count_relations_in_KG() >>>>>>>>>>>>>>>'
    rs = load_relations(literal_relations_file, set())
    frs = load_relations(data_relations_file, rs)
    qid_rel_not_in_KG = set()
    for next_q in wqsp_obj:
        if next_q['QuestionId'] in no_chain_qids:
            continue
        parse_ct, parse_with_good_rels = 0, -1
        for next_parse in next_q['Parses']:
            rel_present = True
            parse_ct += 1
            if next_parse['InferentialChain'] is None or len(next_parse['InferentialChain']) == 0:
                continue
            chain = next_parse['InferentialChain']
            for next_rel in chain:
                nr = 'fb:' + next_rel
                if nr in frs:
                    continue
                rel_present = False
            if rel_present:
                parse_with_good_rels = parse_ct
                break
        if parse_with_good_rels < 0:
            qid_rel_not_in_KG.add(next_q['QuestionId'])
    my_str = bas_utils.to_string(qid_rel_not_in_KG, '\n')
    op_file = open(output_file_chain_not_in_KG, 'w')
    op_file.write(my_str)
    op_file.close()
    print 'len(qid_rel_not_in_KG)=' + str(len(qid_rel_not_in_KG))
    print 'Exiting count_relations_in_KG() <<<<<<<<<<<<<<'
    return qid_rel_not_in_KG


if __name__ == "__main__":
    trn_obj = bas_utils.load_json_file(os.path.join(data_folder, trn_file))
    #trn_obj = bas_utils.load_json_file(os.path.join(data_folder, tst_file))
    print '\nJSON Loaded'
    analyze_data(trn_obj['Questions'])
    ncq = count_no_core_chain(trn_obj['Questions'])
    count_no_topic_ent(trn_obj['Questions'])
    count_no_ans(trn_obj['Questions'])
    count_relations_in_KG(trn_obj['Questions'], ncq)

