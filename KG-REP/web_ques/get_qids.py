"""
0.  First time to create the input_output_file, run function get_initial_list(). Modify the first line for it.
1.  Modify input_output_file
2.  Modify status_folder
3.  Modify qid_prefix
4.  Modify f1 to f4
5.  Refersh cases.txt using /data/Work-Homes/LOD_HOME/FB_SEMPRE/create-subgraph/scr/get_cases_status.sh
"""
import os
import glob
import utils.basics as bas_utils

data_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/'
trn_file = 'WebQSP.train.json'
tst_file = 'WebQSP.test.json'

#input_output_file = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/Train-Data-Analysis.csv'
input_output_file = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/Test-Data-Analysis.csv'

#status_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/train_status'
status_folder = '/data/Work-Homes/LOD_HOME/WebQSP/data/test_status'

#qid_prefix = 'WebQTrn-'
qid_prefix = 'WebQTest-'

#f1 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/trn-no_src-WebQSP.train.json.txt'
#f2 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/trn-no_src_in_kb-WebQSP.train.json.txt'
#f3 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/trn-no_chain-WebQSP.train.json.txt'
#f4 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/trn-no_rel_in_kg-WebQSP.train.json.txt'

f1 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/tst-no_src-WebQSP.test.json.txt'
f2 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/tst-no_src_in_kb-WebQSP.test.json.txt'
f3 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/tst-no_chain-WebQSP.test.json.txt'
f4 = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/all-data/status/tst-no_rel_in_kg-WebQSP.test.json.txt'

final_status_files = [f1, f2, f3, f4]
status = ['No SRC in WebQSP', 'No SRC in KG', 'No Rel in WebQSP', 'No Rel in KG']


max_ct = 4100


def load_final_status():
    my_dict = dict()
    for i in range(0, 4, 1):
        fn = final_status_files[i]
        with open(fn) as f:
            content = f.readlines()
        for next_line in content:
            toks = next_line.split('=')
            val_dict = dict()
            qid = toks[0].replace('\n', '')
            if len(toks) > 1:
                val_dict['reason'] = toks[1].replace('\n', '')
            else:
                val_dict['reason'] = ''
            val_dict['final_status'] = status[i]
            my_dict[qid] = val_dict
    return my_dict


def get_value(a, b):
    if a == '':
        return b
    return a


def get_initial_list():
    next_file = os.path.join(data_folder, tst_file)
    print 'next_file=' + next_file
    q_list = bas_utils.load_json_file(next_file)['Questions']
    print '\nLoaded...'
    qid_set = set()
    for q in q_list:
        qid_set.add(q['QuestionId'])
    output_path_file = os.path.join(data_folder, next_file + '.qid')
    op_file = open(output_path_file, 'w')
    for i in range(0, max_ct, 1):
        qid = qid_prefix + str(i)
        if qid in qid_set:
            op_file.write(qid + '\n')
    op_file.close()


def load_status():
    updated_status = dict()
    for status_file in glob.glob(status_folder + '/*.txt'):
        if status_file.endswith('cases.txt'):
            continue
        next_status_map = load_status_file(status_file)
        for next_qid in next_status_map.keys():
            status_dict = next_status_map[next_qid]
            if next_qid not in updated_status.keys():
                updated_status[next_qid] = status_dict
            else:
                print 'Same QID present in two status files - ' + next_qid + ' =========================== ERROR'
    return updated_status


def load_status_file(status_file_to_load):
    print 'Entering - load_status_file() - ' + status_file_to_load
    status_map = dict()
    with open(status_file_to_load) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split(',')
        if len(toks) < 4:
            continue
        qid = toks[0]
        my_dict = dict()
        my_dict['my_case'] = toks[1]
        my_dict['my_status'] = toks[2]
        my_dict['my_auto_comments'] = toks[3].replace('\n', '')
        if qid not in status_map.keys():
            status_map[qid] = my_dict
        else:
            print 'Same QID present in twice in one status file - ' + qid + ', status-file=' + status_file_to_load \
                  + ' =========================== ERROR'
    print 'status_map size =' + str(len(status_map))
    return status_map


def get_updated_status(new_status, case_status):
    my_status_map, my_header = dict(), ''
    with open(input_output_file) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split(',')
        my_qid = toks[1]
        if my_qid == 'QID':
            my_header = next_line
            continue
        my_dict = dict()
        if my_qid in new_status.keys():
            my_dict['my_case'] = get_value(new_status[my_qid]['my_case'], toks[2])
            my_dict['my_status'] = get_value(new_status[my_qid]['my_status'], toks[3])
            my_dict['my_auto_comments'] = new_status[my_qid]['my_auto_comments']
            my_dict['my_case_comments'] = ''
        else:
            my_dict['my_case'] = toks[2]
            my_dict['my_status'] = toks[3]
            my_dict['my_auto_comments'] = ''
            my_dict['my_case_comments'] = ''
        if my_qid in case_status.keys():
            my_dict['my_case'] = case_status[my_qid]['my_case']
            my_dict['my_status'] = case_status[my_qid]['my_status']
            my_dict['my_case_comments'] = case_status[my_qid]['my_auto_comments']
        my_dict['my_sn'] = toks[0]
        my_dict['my_manual_comments'] = toks[6]
        my_status_map[my_qid] = my_dict
    print 'final status_map size=' + str(len(my_status_map))
    return my_status_map, my_header


def update_status_file(update_status_map, my_header, final_status):
    op_file = open(input_output_file + '.new', 'w')
    op_file.write(my_header)
    print 'len(update_status_map)=' + str(len(update_status_map))
    for i in range(0, max_ct, 1):
        qid = qid_prefix + str(i)
        if qid in update_status_map.keys():
            my_str = update_status_map[qid]['my_sn'] + ',' + qid
            my_str = my_str + ',' + update_status_map[qid]['my_case']
            my_str = my_str + ',' + update_status_map[qid]['my_status']
            my_str = my_str + ',' + get_final_status(final_status, qid)['final_status']
            my_str = my_str + ',' + get_final_status(final_status, qid)['reason']
            my_str = my_str + ',' + update_status_map[qid]['my_auto_comments']
            my_str = my_str + ',' + update_status_map[qid]['my_case_comments']
            my_str = my_str + ',' + update_status_map[qid]['my_manual_comments']
            op_file.write(my_str + '\n')
            #print my_str
    op_file.close()


def get_final_status(status_dict, qid):
    if qid in status_dict.keys():
        status_map = status_dict[qid]
    else:
        status_map = dict()
        status_map['reason'] = ''
        status_map['final_status'] = 'taken'
    return status_map


def main():
    #get_initial_list()
    new_status = load_status()
    final_status = load_final_status()
    # Use scr /data/Work-Homes/LOD_HOME/FB_SEMPRE/create-subgraph/scr to create the cases.txt
    case_status = load_status_file(os.path.join(status_folder, 'cases.txt'))
    status_map, my_header = get_updated_status(new_status, case_status)
    update_status_file(status_map, my_header, final_status)
    os.rename(input_output_file, input_output_file + '.bkp')
    os.rename(input_output_file + '.new', input_output_file)


if __name__ == '__main__':
    main()
