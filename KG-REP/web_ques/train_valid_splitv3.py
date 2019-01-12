"""
1.  For now putting all the C7, C8 and C9 in tst-no_src_in_kb-WebQSP.test.json.txt and trn-no_src_in_kb-WebQSP.train.json.txt files
    This is so because qid-sid map file does not contain their sid.
2.
"""

import os
import json
import random
import utils.basics as bas_utils
import utils.my_map as mm
import kgrep.load_prepare_data as lpd


data_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/'
trn_file = 'WebQSP.train.json'
tst_file = 'WebQSP.test.json'
final_qid_sid_map_file = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data-3/final_qid_sid_mapping.txt'

#node_map_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/node-map-subg2.rdf'
#rel_map_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/rel-map-subg2.rdf'

node_map_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data-3/node-map-subg3.rdf'
rel_map_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data-3/rel-map-subg3-manual.rdf'


#new_rel_map_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/new-rels.txt'

valid_size = 0

#output_path = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/'
#output_path = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/split-6/'
output_path = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/split-7/'

#output_w2v_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/all_words/webqsp_qm.txt'
output_w2v_pf = output_path + 'webqsp_qm.txt'

include_case_1789 = True


def get_my_json(web_qsp_file, qid_sid_map, prefix):
    print '1: web_qsp_file=' + web_qsp_file
    my_list = list()
    json_obj = bas_utils.load_json_file(web_qsp_file)
    no_src_ct, no_chain_ct, no_src_ent_in_kb_ct, total_ct = 0, 0, 0, 0
    pf = os.path.basename(web_qsp_file)
    no_src_file = open(os.path.join(output_path, 'status', prefix + '-no_src-' + pf + '.txt'), 'w')
    no_chain_file = open(os.path.join(output_path, 'status', prefix + '-no_chain-' + pf + '.txt'), 'w')
    no_src_in_kb_file = open(os.path.join(output_path, 'status', prefix + '-no_src_in_kb-' + pf + '.txt'), 'w')
    for next_q in json_obj['Questions']:
        total_ct += 1
        qid = next_q['QuestionId']
        if next_q['Parses'][0]['TopicEntityMid'] is None or len(next_q['Parses'][0]['TopicEntityMid']) < 1:
            ### CASE-1
            no_src_ct += 1
            no_src_file.write(next_q['QuestionId'] + '\n')
            continue
        if next_q['Parses'][0]['InferentialChain'] is None or len(next_q['Parses'][0]['InferentialChain']) < 1:
            ### CASE-2
            no_chain_file.write(next_q['QuestionId'] + '\n')
            no_chain_ct += 1
            continue
        src_ent_mid = 'fb:' + next_q['Parses'][0]['TopicEntityMid']
        myq = dict()
        if qid not in qid_sid_map.keys():
            no_src_ent_in_kb_ct += 1
            no_src_in_kb_file.write(next_q['QuestionId'] + '\n')
            myq['src_ent'] = ''
        else:
            myq['src_ent'] = qid_sid_map[qid]
        myq['qid'] = next_q['QuestionId']
        #myq['qo'] = next_q['RawQuestion'].encode('utf8').lower()
        myq['qo'] = next_q['ProcessedQuestion']
        #myq['src_ent'] = mid2sid[src_ent_mid]
        myq['rel_seq'] = next_q['Parses'][0]['InferentialChain']
        myq['PotentialTopicEntityMention'] = next_q['Parses'][0]['PotentialTopicEntityMention']
        myq['TopicEntityName'] = next_q['Parses'][0]['TopicEntityName']
        myq['ProcessedQuestion'] = next_q['ProcessedQuestion']
        my_list.append(myq)
    no_src_file.close()
    no_chain_file.close()
    no_src_in_kb_file.close()
    print '\n1: get_my_json(): no_src_ct(Rejected)=' + str(no_src_ct)
    print '1: get_my_json(): no_chain_ct(Rejected)=' + str(no_chain_ct)
    print '1: get_my_json(): no_src_ent_in_kb_ct=' + str(no_src_ent_in_kb_ct)
    print '1: get_my_json(): Total Rejected =' + str(int(no_src_ct + no_chain_ct))
    print '1: get_my_json(): ' + str(web_qsp_file) + ' --> ' + str(len(my_list)) + ' / ' + str(total_ct)
    return my_list


def split_train_valid(data_list):
    random.shuffle(data_list)
    given_train_size = len(data_list)
    splitted_train_size = given_train_size * (100-valid_size) / 100
    train_split = data_list[:splitted_train_size]
    valid_split = data_list[splitted_train_size:]
    if valid_size == 0:
        train_split = data_list
        valid_split = data_list[-1:]
    return train_split, valid_split


def load_node_map():
    ct = 0
    node_map = mm.my_map(-1)
    with open(node_map_pf) as f:
        content = f.readlines()
    for next_line in content:
        ct += 1
        toks = next_line.split()
        kg_node = toks[0]
        node_id = toks[1]
        node_map.set(kg_node, node_id)
        bas_utils.print_status(' load_node_map()          ', ct, 1)
    print "\nNodes Loaded....."
    return node_map


def load_rel_map():
    rel_map = dict()
    ct = 0
    with open(rel_map_pf) as f:
        content = f.readlines()
    for next_line in content:
        ct += 1
        toks = next_line.split()
        kg_rel_name = toks[0]
        rel_id = toks[1]
        rel_map[kg_rel_name] = rel_id
        bas_utils.print_status(' load_rel_map()          ', ct, 1)
#    with open(new_rel_map_pf) as f:
#        content = f.readlines()
#    for next_line in content:
#        ct += 1
#        toks = next_line.split()
#        kg_rel_name = toks[0]
#        rel_id = toks[1]
#        rel_map[kg_rel_name] = rel_id
#        bas_utils.print_status(' load_rel_map()          ', ct, 1)
    print "\nRelations Loaded....."
    return rel_map


def replace_ent_in_question(qid_sid_map, qid_map, node_map):
    print "\nEntering replace_ent_in_question()"
    ct = 0
    for qid in qid_map.keys():
        ct += 1
        next_obj = qid_map[qid]
        if qid not in qid_sid_map.keys() or qid_map[qid]['src_ent'] is None or qid_map[qid]['src_ent'] == '':
            qid_map[qid]['er_status'] = 2
            se = '_MYENTMENTION_'
            if not include_case_1789:
                continue
        else:
            ent_name = qid_sid_map[qid]
            se = node_map.get(ent_name)
        qid_map[qid]['qm'] = str(next_obj['qo']).replace(next_obj['PotentialTopicEntityMention'], se + ' ')
    return qid_map


def get_qid_status(row_status, qid_status):
    return max(row_status, qid_status)


def er_summary(qid_map, qid_not_in_map):
    my_status = [0, 0, 0, 0, 0]
    for qid in qid_map.keys():
        if 'er_status' in qid_map[qid].keys():
            my_status[qid_map[qid]['er_status']] += 1
        else:
            my_status[0] += 1
            print 'ER1--> ' + qid
    print '2: Summary --> ' + bas_utils.to_string(my_status, ', ')


def add_rel_id(web_qsp_file, rel_map, qmap, unfound_rels, prefix):
    unfound_rel_q_ct = 0
    no_chain_count, qid_for_no_rel_in_kg,  = 0, dict()
    pf = os.path.basename(web_qsp_file)
    for next_qid in qmap.keys():
        next_q = qmap[next_qid]
        if 'rel_seq' not in next_q.keys():
            # Does not come here, because we did not add the Case-2 QIDs in the qmap
            print '3: No Chain Present - ' + next_qid
            no_chain_count += 1
            continue
        rel_seq = next_q['rel_seq']
        rid_seq = list()
        rel_found = True
        for next_rel in rel_seq:
            nr = 'fb:' + next_rel
            if nr not in rel_map.keys():
                print 'Relation Not Found = ' + nr + ', for qid=' + next_qid
                add_to_dict(qid_for_no_rel_in_kg, next_qid, nr)
                unfound_rels.add(nr)
                rel_found = False
            else:
                rid_seq.append(rel_map[nr])
            if not rel_found:
                unfound_rel_q_ct += 1
        next_q['rid_seq'] = rid_seq
        qmap[next_qid] = next_q
    no_rel_in_kg_file = open(os.path.join(output_path, 'status', prefix + '-no_rel_in_kg-' + pf + '.txt'), 'w')
    no_rel_in_kg_file.write(bas_utils.to_string_dict(qid_for_no_rel_in_kg, '\n'))
    print '3: add_rel_id() - unfound_rel q ct=' + str(unfound_rel_q_ct)
    print '3: add_rel_id() - no_chain_count=' + str(no_chain_count)
    print '3: add_rel_id() - end - len(unfound_rels)=' + str(len(unfound_rels))
    return qmap, unfound_rels


def add_to_dict(my_dict, k, v):
    if k in my_dict.keys():
        old_value = my_dict[k]
    else:
        old_value = ''
    new_value = str(old_value + ',' + v)
    if new_value.startswith(','):
        new_value = new_value[1:]
    my_dict[k] = new_value
    return my_dict


def add_src_ids(qmap, node_map):
    for next_qid in qmap.keys():
        next_q = qmap[next_qid]
        src_ent = next_q['src_ent']
        if src_ent is None or src_ent == '' or not node_map.contains_key(src_ent):
            if not include_case_1789:
                continue
            next_q['src_ent_id'] = '_MYENTMENTION_'
            next_q['src_ent'] = '_MYENTMENTION_'
        else:
            next_q['src_ent_id'] = node_map.get(src_ent)
        qmap[next_qid] = next_q
    return qmap


def check_final_old(qmap):
    for qid in qmap.keys():
        q_obj = qmap[qid]
        rel_seq = q_obj['rel_seq']
        rid_seq = q_obj['rid_seq']
        if len(rel_seq) == len(rid_seq):
            is_ready = 1
        else:
            is_ready = 0
        if 'qm' in q_obj.keys() and is_ready == 1:
            is_ready = 1
        else:
            is_ready = 0
        if is_ready and 'src_ent_id' in q_obj.keys():
            is_ready = 1
        else:
            is_ready = 0
        q_obj['is_ready'] = is_ready
        qmap[qid] = q_obj
    return qmap


def post_process(qmap):
    """
    Replace the PotentialTopicEntityMention of the question by a _MYENTMENTION_ token
    """
    for qid in qmap.keys():
        next_obj = qmap[qid]
        if 'er_status' in next_obj.keys() and next_obj['er_status'] == 2:
            q = str(next_obj['qo']).replace(next_obj['PotentialTopicEntityMention'], '_MYENTMENTION_')
            next_obj['qo'] = q
            qmap[qid] = next_obj
    return qmap


def check_final(qmap):
    print 'check_final --> Entering'
    my_status = [0, 0, 0, 0, 0]
    for qid in qmap.keys():
        if 'er_status' in qmap[qid].keys():
            my_status[qmap[qid]['er_status']] += 1
        else:
            my_status[0] += 1
        q_obj = qmap[qid]
        rel_seq = q_obj['rel_seq']
        rid_seq = q_obj['rid_seq']
        if len(rel_seq) == len(rid_seq):
            is_ready = 1
        else:
            is_ready = 0
        if 'qm' in q_obj.keys() and is_ready == 1:
            is_ready += 1
        if is_ready > 1 and 'src_ent_id' in q_obj.keys():
            is_ready += 1
        q_obj['is_ready'] = is_ready
        qmap[qid] = q_obj
        if 'er_status' in q_obj.keys() and q_obj['er_status'] == 0:
            print 'ER1 --> ' + qid
    print 'check_final: Summary --> ' + bas_utils.to_string(my_status, ', ')
    print 'check_final --> Exiting'
    return qmap


def convert_list_2_dict(my_list):
    my_map = dict()
    for nextq in my_list:
        qid = nextq['qid']
        my_map[qid] = nextq
    return my_map


def convert_dict_2_list(my_dict):
    my_list = list()
    for k in my_dict.keys():
        my_list.append(my_dict[k])
    return my_list


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


def print_quest_4_w2v(allq):
    op_file = open(output_w2v_pf, 'w')
    for nextq in allq:
        if 'qm' in nextq.keys():
            op_file.write(nextq['qm'] + '\n')
    op_file.close()


def load_qid_sid_map():
    my_map = dict()
    with open(final_qid_sid_map_file) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split(',')
        qid = toks[0]
        sid = toks[1].replace('\n', '')
        my_map[qid] = sid
    return my_map


def check_basics():
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    status_folder = os.path.join(output_path, 'status')
    if not os.path.isdir(status_folder):
        os.mkdir(status_folder)


def main():
    check_basics()
    nm = load_node_map()
    rm = load_rel_map()
    qid_sid_map = load_qid_sid_map()
    trn_path_file = os.path.join(data_folder, trn_file)

    trn_json = get_my_json(trn_path_file, qid_sid_map, 'trn')  #
    trn_map = convert_list_2_dict(trn_json)
    # Include 'qm' in the json, if src ent present in node-map
    trn_map_nid = replace_ent_in_question(qid_sid_map, trn_map, nm)  #
    trn_map_rid, unfound_rels = add_rel_id(trn_path_file, rm, trn_map_nid, set(), 'trn')
    trn_map_src = add_src_ids(trn_map_rid, nm)
    #trn_map_post = post_process(trn_map_src)
    trn_map_final = check_final(trn_map_src)
    final_trn_list = convert_dict_2_list(trn_map_final)
    print_json(os.path.join(output_path, 'all.kgt_trn.json'), final_trn_list)
    trn, val = split_train_valid(final_trn_list)
    print_json(os.path.join(output_path, 'kgt_trn.json'), trn)
    print_json(os.path.join(output_path, 'kgt_val.json'), val)

    tst_path_file = os.path.join(data_folder, tst_file)
    tst_json = get_my_json(tst_path_file, qid_sid_map, 'tst')
    tst_map = convert_list_2_dict(tst_json)
    tst_map_nid = replace_ent_in_question(qid_sid_map, tst_map, nm)
    tst_map_rid, unfound_rels = add_rel_id(tst_path_file, rm, tst_map_nid, unfound_rels, 'tst')
    tst_map_src = add_src_ids(tst_map_rid, nm)
    tst_map_final = check_final(tst_map_src)
    final_tst_list = convert_dict_2_list(tst_map_final)
    print_json(os.path.join(output_path, 'kgt_tst.json'), final_tst_list)
    print 'len(unfound_rels)=' + str(len(unfound_rels))
    new_rel_str = bas_utils.to_string(unfound_rels, '\n')
    f = open(os.path.join(output_path, 'new-rels.txt'), 'w')
    f.write(new_rel_str + '\n')
    f.close()

    all_q = final_trn_list + final_tst_list
    print_quest_4_w2v(all_q)


if __name__ == '__main__':
    main()
