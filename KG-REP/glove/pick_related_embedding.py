import os
import sys
import numpy as np
from utils import basics as bas_utils

dp_home, trn_file, val_file, tst_file, rel_tok_file, oov_pf, output_pf, all_q_file = '', '', '', '', '', '', '', ''
ere_embedding_file, question_key = '', ''


def check_input_arguments():
    if len(sys.argv) < 4:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <dp_name> <question-key-in-json> <output_folder_suffix>\n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python ' + sys.argv[0] + ' webqsp ProcessedQuestion model/ere-glove \n')
        sys.stderr.write('python ' + sys.argv[0] + ' fb15k fq model/ere-glove \n')
        sys.exit(1)
    global dp_home, trn_file, val_file, tst_file, rel_tok_file, oov_pf, output_pf, all_q_file, question_key
    global ere_embedding_file
    dp_name = sys.argv[1]
    print 'dp_name=', dp_name
    dp_home = os.path.join(os.environ['WORK_DIR'], dp_name)
    print 'dp_home=', dp_home
    trn_file = os.path.join(dp_home, 'input_data', 'kgt_trn.json')
    val_file = os.path.join(dp_home, 'input_data', 'kgt_val.json')
    tst_file = os.path.join(dp_home, 'input_data', 'kgt_tst.json')
    rel_tok_file = os.path.join(dp_home, 'kg', 'rel_toks.txt')
    oov_pf = os.path.join(os.environ['WORK_DIR'], 'wikipedia', dp_name + '-OOV.txt')
    ere_embedding_file = os.path.join(os.environ['WORK_DIR'], 'wikipedia/glove/glove.6B.300d.txt')
    output_pf = os.path.join(dp_home, sys.argv[3], 'glove.txt')
    all_q_file = os.path.join(dp_home, 'input_data', 'all_queries.txt')
    question_key = sys.argv[2]
    print_variables()


def print_variables():
    print '==================================================================================='
    print '1. dp_home = ' + dp_home
    print '2. trn_file = ' + trn_file
    print '3. val_file = ' + val_file
    print '4. tst_file = ' + tst_file
    print '5. rel_tok_file = ' + rel_tok_file
    print '6. oov_pf = ' + oov_pf
    print '7. output_pf = ' + output_pf
    print '8. all_q_file = ' + all_q_file
    print '9. question_key = ' + question_key
    print '==================================================================================='


def main():
    wi_rel = get_rel_toks(dict(), 1)
    wi_trn = get_word_index(trn_file, wi_rel, len(wi_rel))
    wi_tst = get_word_index(tst_file, wi_trn, len(wi_trn))
    wi = get_word_index(val_file, wi_tst, len(wi_trn))
    print '\ntotal input word count = ' + str(len(wi))
    if 'belong' in wi.keys():
        print 'belong in wi --------------------'
    em = get_glove_embed(wi)
    write_embd(wi, em)


def get_json_obj(path_file):
    if path_file.find('subgraph_webq') > 0:
        json_obj = bas_utils.load_json_file(path_file)['Questions']
    else:
        json_obj = bas_utils.load_json_file(path_file)
    return json_obj


def load_my_q():
    print '\nEntering - load_my_q()'
    i = 0
    sint = bas_utils.ignore_exception(ValueError)(int)
    my_words_qm = set()
    with open(all_q_file) as f:
        content = f.readlines()
    for next_line in content:
        nl = next_line.lower()
        i += 1
        toks = nl.split()
        for w in toks:
            if w.startswith("e"):
                remw = w[1:]
                if sint(remw) is not None:
                    continue
            if w in my_words_qm:
                continue
            my_words_qm.add(w)
        bas_utils.print_status('load_my_q()', i, 1)
    return my_words_qm


def get_word_index(path_file, word_index, ct):
    print '\nEntering - get_word_index() for - ' + path_file
    sint = bas_utils.ignore_exception(ValueError)(int)
    json_obj = get_json_obj(path_file)
    for next_obj in json_obj:
        q = next_obj[question_key]
        qt = q.replace(',', ' ')
        q = qt.lower()
        toks = q.split()
        for w in toks:
            if w in word_index.keys():
                continue
            if w.startswith('e') and sint(w[1:]) is not None:
                continue
            ct += 1
            word_index[w] = ct
    return word_index


def get_rel_toks(word_index, ct):
    print '\nEntering - get_rel_toks()'
    i = 0
    with open(rel_tok_file) as f:
        content = f.readlines()
    for next_line in content:
        i += 1
        rel_toks = next_line.split(';')[0].split()
        for w in rel_toks:
            if w in word_index.keys():
                continue
            ct += 1
            word_index[w] = ct
        bas_utils.print_status('get_rel_toks()', i, 1)
    return word_index


def get_glove_embed(wi):
    ct, i, idx = 0, 0, 0
    oov = set(wi.keys())
    embedding_matrix = np.zeros((len(wi) + 1, 300))
    qm_word = load_my_q()
    qms = len(qm_word)
    with open(ere_embedding_file) as f:
        content = f.readlines()
    for next_line in content:
        msg = 'i=' + str(i) + ', idx=' + str(idx) + ' / ' + str(len(wi))
        bas_utils.print_status(msg + '  get_glove_embed()', ct, 1)
        i += 1
        toks = next_line.split()
        w = toks[0]
        my_words = wi.keys()
        if w not in my_words:
            continue
        oov.remove(w)
        if w in qm_word:
            qm_word.remove(w)
        ct += 1
        idx = wi[w]
        embedding_matrix[idx] = np.asarray(toks[1:], dtype=float)
    print '\nct=' + str(ct) + ', i=' + str(i)
    print 'OOV Count = ' + str(len(oov)) + ' / ' + str(len(wi.keys()))
    print 'OOV Count = ' + str(len(qm_word)) + ' / ' + str(qms)
    oov_str = bas_utils.to_string(qm_word, '\n')
    f = bas_utils.open_file(oov_pf)
    f.write(oov_str + '\n')
    f.close()
    return embedding_matrix


def write_embd(wi, e_mat):
    op_file = open(output_pf, 'w')
    my_words = wi.keys()
    for w in my_words:
        idx = wi[w]
        e = e_mat[idx]
        next_line = w + ' ' + bas_utils.to_string(my_list=e, separator=' ') + '\n'
        op_file.write(next_line)
    op_file.close()
    print 'Output written to file - ' + output_pf


if __name__ == '__main__':
    check_input_arguments()
    main()
