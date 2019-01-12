import os

data_folder = '/data/Work-Homes/LOD_HOME/web-questions/S-Mart-Entity-Linking/STAGG-master'

"""
in the STAGG folder there are two files or train and test splits
Test - webquestions.examples.test.e2e.top10.filter.tsv and webquestions.examples.test.e2e.top10.filter.sid.tsv
Train - webquestions.examples.train.e2e.top10.filter.tsv and webquestions.examples.train.e2e.top10.filter.sid.mod.tsv

One of these files contains mid against an EDL entity and another one contains corresponding sid.

This program prepares a map with key as mid, and value as sid using these two pairs of files.   
"""



def read_file(path_file):
    my_list = list()
    with open(path_file) as f:
        content = f.readlines()
    for next_line in content:
        my_list.append(next_line)
    return my_list


def match_rows(sid_row, mid_row):
    has_matched = True
    mid_toks = mid_row.split('\t')
    sid_toks = sid_row.split('\t')
    for i in range(6):
        if mid_toks[i] == sid_toks[i] or i == 4:
            continue
        else:
            print 'mid - ' + mid_toks[i]
            print 'sid - ' + sid_toks[i]
            has_matched = False
            break
    return has_matched, mid_toks[4], sid_toks[4]


def map_sid_mid(mid_fn, sid_fn):
    mid_path_file = os.path.join(data_folder, mid_fn)
    sid_path_file = os.path.join(data_folder, sid_fn)
    my_map = dict()
    sid_list = read_file(sid_path_file)
    mid_list = read_file(mid_path_file)
    max_ct = max(len(sid_list), len(mid_list))
    for i in range(max_ct):
        has_matched, mid, sid = match_rows(sid_list[i], mid_list[i])
        if not has_matched:
            print '==================== UN-Matched Rows ============================='
            print 'sid row = ' + sid_list[i]
            print 'mid row = ' + mid_list[i]
            print 'line number = ' + str(i+1)
            print '=================================================================='
            break
        my_map[mid] = sid
    return my_map


def get_sid_2_mid_all():
    mid_fn = 'webquestions.examples.test.e2e.top10.filter.tsv'
    sid_fn = 'webquestions.examples.test.e2e.top10.filter.sid.tsv'
    trn_map = map_sid_mid(mid_fn, sid_fn)
    mid_fn = 'webquestions.examples.train.e2e.top10.filter.tsv'
    sid_fn = 'webquestions.examples.train.e2e.top10.filter.sid.mod.tsv'
    tst_map = map_sid_mid(mid_fn, sid_fn)
    for next_mid in tst_map.keys():
        if next_mid in trn_map.keys():
            if tst_map[next_mid] != trn_map[next_mid]:
                print 'mapping error for mid = ' + next_mid
                print 'tst_map[next_mid]=' + tst_map[next_mid]
                print 'trn_map[next_mid]=' + trn_map[next_mid]
        trn_map[next_mid] = tst_map[next_mid]
    return trn_map


if __name__ == "__main__":
    all_map = get_sid_2_mid_all()
    print 'all_map['+all_map.keys()[0] + ']=' + all_map[all_map.keys()[0]]