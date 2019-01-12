import os
import re
import sys
import json
import utils.basics as ub
import get_kbqa_path_gt as kbqa_prog

output_dir = '/data/Work-Homes/LOD_HOME/KBQA_RE_data/KBQA_RE_data-master/webqsp_relations/'
web_questions_path = '/data/Work-Homes/LOD_HOME/web-questions/data/'
stagg_dir = '/data/Work-Homes/LOD_HOME/web-questions/S-Mart-Entity-Linking/STAGG-master/'


def read_data(file_name):
    json_string = ''
    with open(file_name) as f:
        content = f.readlines()
    for next_line in content:
        json_string += next_line
    my_data_obj = json.loads(json_string)
    return my_data_obj


def merge_data(training_data, test_data):
    all_data = list()
    ct = 0
    for next_q in training_data:
        next_q['id'] = 'WebQTrn-' + str(ct)
        next_q['s1'] = 'WebQTrn-' + str(ct)
        all_data.append(next_q)
        ct += 1
    ct = 0
    for next_q in test_data:
        next_q['id'] = 'WebQTest-' + str(ct)
        all_data.append(next_q)
        ct += 1
    print training_data[100]['utterance'] + '----' + training_data[100]['id']
    return all_data


def load_entities(fn, my_dict):
    path_file = os.path.join(stagg_dir, fn)
    with open(path_file) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split('\t')
        my_key = toks[0]
        sf = toks[1]
        if my_key in my_dict.keys():
            my_ent_set = my_dict[my_key]
        else:
            my_ent_set = set()
        my_ent_set.add(sf)
        my_dict[my_key] = my_ent_set
    return my_dict


def map_webq_kbqa():
    training_data = read_data(os.path.join(web_questions_path, 'webquestions.examples.train.json'))
    test_data = read_data(os.path.join(web_questions_path, 'webquestions.examples.train.json'))
    webq_list = merge_data(training_data, test_data)
    trn_ent = load_entities('webquestions.examples.train.e2e.top10.filter.sid.tsv', dict())
    given_ent = load_entities('webquestions.examples.test.e2e.top10.filter.sid.tsv', trn_ent)
    all_ent = load_entities('remain.tsv', given_ent)
    kbqa_list = kbqa_prog.get_kbqa_data()
    for next_webqa in webq_list:
        print next_webqa['id'] + '-' + ub.to_string(all_ent[next_webqa['id']])
        for next_kbqa in kbqa_list:
            wq = re.sub('[^a-zA-Z0-9 ]', '', next_webqa['utterance'])
            is_matched = match_question_pattern(wq, next_kbqa['ques'], all_ent[next_webqa['id']])
            if is_matched and 'kbqa_id' in next_webqa.keys():
                next_webqa['kbqa_id'] = next_webqa['kbqa_id'] + ';' + next_kbqa['id']
            if is_matched:
                next_webqa['kbqa_id'] = next_kbqa['id']


def match_question_pattern(question, pattern, my_ents):
    ques_toks = question.split()
    patt_toks = pattern.split()
    i, j = 0, 1
    while i < len(ques_toks):
        #print ques_toks[i] + '-' + patt_toks[j]
        if patt_toks[j] != ques_toks[i] and patt_toks[j] != '<e>':
            return False
        if patt_toks[j] == '<e>':
            is_matched, tok_ct = match_entity(question, pattern[6:], my_ents)
            if is_matched:
                i += (tok_ct - 1)
        j += 1
        i += 1
    return True


def match_entity(quest, patt, my_ents):
    patt_ent_pos = patt.find('<e>')
    remain_quest = quest[patt_ent_pos:]
    for next_ent in my_ents:
        if str(remain_quest).startswith(next_ent):
            ct = len(next_ent.split())
            return True, ct
    return False, 0


if __name__ == "__main__":
    map_webq_kbqa()
