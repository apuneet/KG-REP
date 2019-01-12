"""
1.  Modify function pre_process_outputs() for relation map file

"""
import os
import re
import argparse
import numpy as np
from shutil import copyfile
import utils.basics as bas_utils
from keras.preprocessing.sequence import pad_sequences

fns = ['kgt_trn.json', 'kgt_val.json', 'kgt_tst.json']


def parse_args():
    parser = argparse.ArgumentParser(description="Load and Prepare data")
    parser.add_argument('--dp_name', nargs='?', default='fb15k2', help='Data Package Name, e.g., fb15k2')
    parser.add_argument('--input-path', nargs='?', default='/data/Work-Homes/LOD_HOME/fb15k/data-wip/queries/questions/',
                        help='Input queries file path, this folder should contain ' +
                             'kgt_test.csv, kgt_train.csv, and kgt_valid.csv')
    parser.add_argument('--output', nargs='?', default='kgt_op/op.seq.txt',
                        help='Output Filename with Path, relative to LOD_HOME/DP_NAME/')
    parser.add_argument('--word-embedding', nargs='?', default='model/merged_embd/m.embd',
                        help='Embedding Filename with Path, relative to LOD_HOME/DP_NAME/')
    return parser.parse_args()


def main(my_args):
    '''
    osl --> Output Sequence Length
    :param my_args:
    :return:
    '''
    print 'Entering - load_prepare_data.main()'
    if my_args.p['load_command'] == 0:
        return load_saved_data(my_args)
    fn = os.path.basename(my_args.p['conf_file'])
    copyfile(my_args.p['conf_file'], os.path.abspath(os.path.join(my_args.job_folder, os.pardir, 'saved_data', fn)))

    x_all, y_all, src_ent_all, max_sen_len, max_osl, jos, qs = load_data(my_args)
    em_dim, word_index, em_mat, rel_mat = load_embeddings(my_args)
    print 'Embeddings loaded, starting to pre-process inputs and outputs...'
    x_all_padded, jos = pre_process_inputs(my_args, x_all, word_index, max_sen_len, my_args, jos, qs)
    np_y_all = pre_process_outputs(my_args, y_all, word_index, em_mat, rel_mat, max_osl, max_sen_len)
    rel_tok_seqs, rel_ids = pre_process_relations(word_index, max_sen_len)
    if my_args.p['load_command'] == 1:
        save_data(my_args, em_dim, word_index, em_mat, rel_mat, max_sen_len, x_all_padded, np_y_all, y_all,
                  src_ent_all, max_osl, jos, qs, rel_tok_seqs, rel_ids)
    print 'Exiting - load_prepare_data.main()'
    return em_dim, word_index, em_mat, rel_mat, max_sen_len, x_all_padded, np_y_all, y_all, src_ent_all, max_osl, jos, \
           qs, rel_tok_seqs, rel_ids


def save_data(this_args, embd_dim, word_index, embedding_matrix, rel_embd_mat, max_sen_len, x_all_padded, np_y_all, y_all,
              src_ent_all, max_osl, json_objs, qid_seqs, rel_tok_seqs, rel_ids):
    print 'Entering save_data()'
    op_path = os.path.abspath(os.path.join(this_args.job_folder, os.pardir, 'saved_data'))
    op_file = open(os.path.join(op_path, 'vars.txt'), 'w')
    op_file.write('embd_dim='+str(embd_dim) + '\n')
    op_file.write('max_sen_len=' + str(max_sen_len) + '\n')
    op_file.write('max_osl=' + str(max_osl) + '\n')
    op_file.close()
    bas_utils.save_2_pickle(word_index, os.path.join(op_path, 'word_index.pickle'))
    bas_utils.save_2_pickle(embedding_matrix, os.path.join(op_path, 'embedding_matrix.pickle'))
    bas_utils.save_2_pickle(rel_embd_mat, os.path.join(op_path, 'rel_embd_mat.pickle'))
    bas_utils.save_2_pickle(x_all_padded, os.path.join(op_path, 'x_all_padded.pickle'))
    bas_utils.save_2_pickle(np_y_all, os.path.join(op_path, 'np_y_all.pickle'))
    bas_utils.save_2_pickle(y_all, os.path.join(op_path, 'y_all.pickle'))
    bas_utils.save_2_pickle(src_ent_all, os.path.join(op_path, 'src_ent_all.pickle'))
    bas_utils.save_2_pickle(rel_tok_seqs, os.path.join(op_path, 'rel_tok_seqs.pickle'))
    bas_utils.save_2_pickle(rel_ids, os.path.join(op_path, 'rel_ids.pickle'))
    for i in range(len(fns)):
        bas_utils.save_json_to_file(json_objs[i], os.path.join(op_path, fns[i]))
    bas_utils.save_2_pickle(qid_seqs, os.path.join(op_path, 'qid_sqs.pickle'))
    print 'Exiting save_data()'


def load_saved_data(this_args):
    if 'saved_data' in this_args.p.keys():
        op_path = os.path.abspath(this_args.p['saved_data'])
    else:
        op_path = os.path.abspath(os.path.join(this_args.job_folder, os.pardir, 'saved_data'))
    word_index = bas_utils.load_pickle_file(os.path.join(op_path, 'word_index.pickle'))
    embed_mat = bas_utils.load_pickle_file(os.path.join(op_path, 'embedding_matrix.pickle'))
    rel_mat = bas_utils.load_pickle_file(os.path.join(op_path, 'rel_embd_mat.pickle'))
    x_all_padded = bas_utils.load_pickle_file(os.path.join(op_path, 'x_all_padded.pickle'))
    np_y_all = bas_utils.load_pickle_file(os.path.join(op_path, 'np_y_all.pickle'))
    y_all = bas_utils.load_pickle_file(os.path.join(op_path, 'y_all.pickle'))
    src_ent_all = bas_utils.load_pickle_file(os.path.join(op_path, 'src_ent_all.pickle'))
    rel_tok_seqs = bas_utils.load_pickle_file(os.path.join(op_path, 'rel_tok_seqs.pickle'))
    rel_ids = bas_utils.load_pickle_file(os.path.join(op_path, 'rel_ids.pickle'))
    embd_dim, max_sen_len, max_osl = 0, 0, 0
    with open(os.path.join(op_path, 'vars.txt')) as f:
        content = f.readlines()
    for next_line in content:
        if next_line.startswith('embd_dim='):
            embd_dim = int(next_line.split('=')[1].replace('\n', ''))
        if next_line.startswith('max_sen_len='):
            max_sen_len = int(next_line.split('=')[1].replace('\n', ''))
        if next_line.startswith('max_osl='):
            max_osl = int(next_line.split('=')[1].replace('\n', ''))
    jos = list()
    for fn in fns:
        json_obj = bas_utils.load_json_file(os.path.join(op_path, fn))
        jos.append(json_obj)
    qs = bas_utils.load_pickle_file(os.path.join(op_path, 'qid_sqs.pickle'))
    print 'Returning from Saved Data ...'
    return embd_dim, word_index, embed_mat, rel_mat, max_sen_len, x_all_padded, np_y_all, y_all, src_ent_all, max_osl, jos, \
           qs, rel_tok_seqs, rel_ids


def load_data(my_args):
    if os.path.isfile(os.path.join(my_args.input_path, 'kgt_train.csv')):
        x_all, y_all, src_ent_all, max_sen_len, max_op_seq_length, json_objs, qs = load_data_csv(my_args)
    else:
        x_all, y_all, src_ent_all, max_sen_len, max_op_seq_length, json_objs, qs = load_data_json(my_args)
    return x_all, y_all, src_ent_all, max_sen_len, max_op_seq_length, json_objs, qs


def load_data_csv(my_args):
    print 'load_file_set() Loading Questions from Path - ' + my_args.input_path
    x_all, y_all, src_ent_all, max_sen_len = [], [], [], 0
    csv_fns = ['kgt_train.csv', 'kgt_valid.csv', 'kgt_test.csv']
    for fn in csv_fns:
        queries, ans_seq, src_ents = [], [], []
        with open(os.path.join(my_args.input_path, fn)) as f:
            content = f.readlines()
        for a_line in content:
            q_a = a_line.replace('\n', '').split(';')
            queries.append(q_a[0])
            src_ents.append(q_a[1:3])
            ans_seq.append(q_a[3:])
            max_sen_len = max(len(a_line), max_sen_len)
        x_all.append(queries)
        y_all.append(ans_seq)
        src_ent_all.append(src_ents)
    return x_all, y_all, src_ent_all, max_sen_len, 4, None, None


def load_data_json(my_args):
    print 'load_data_from_json() Loading Questions from Path - ' + my_args.input_path
    x_all, y_all, src_ent_all, max_sen_len, max_op_seq_length, json_objs, qid_seqs = [], [], [], 0, 0, list(), list()
    for fn in fns:
        queries, ans_seq, src_ents, qid_seq = [], [], [], list()
        json_obj = bas_utils.load_json_file(os.path.join(my_args.input_path, fn))
        json_objs.append(bas_utils.convert_list_2_dict(json_obj, 'qid'))
        for nextq in json_obj:
            if nextq['is_ready'] < 2:
                continue
            if 'qm' not in nextq.keys():
                print 'No QM - in ' + nextq['qid']
            queries.append(nextq['qm'])
            se = nextq['src_ent_id']
            if not isinstance(se, list):
                se_list = [se]
            else:
                se_list = se
            src_ents.append(se_list)
            ans_seq.append(nextq['rid_seq'])
            max_sen_len = max(len(str(nextq['qm']).split()), max_sen_len)
            max_op_seq_length = max(len(nextq['rid_seq']), max_op_seq_length)
            qid_seq.append(nextq['qid'])
        x_all.append(queries)
        y_all.append(ans_seq)
        src_ent_all.append(src_ents)
        qid_seqs.append(qid_seq)
    print '\n\nInput Sequence Length = ' + str(max_sen_len)
    return x_all, y_all, src_ent_all, max_sen_len, max_op_seq_length, json_objs, qid_seqs


def load_embeddings_old(my_args):
    print 'load_embeddings() Loading Embeddings from - ' + my_args.word_embedding
    word_index, word_count, embd_dim = {}, 0, 0
    f = open(my_args.word_embedding)
    for a_line in f:
        if len(a_line.split()) < 3:
            continue
        word_count += 1
        if embd_dim == 0:
            embd_dim = len(a_line.split(' ')) - 1
    f.close()
    print('Found %s word vectors.' % word_count)
    embedding_matrix = np.zeros((word_count + 1, embd_dim))
    ct = 0
    with open(my_args.word_embedding) as f:
        content = f.readlines()
    for next_line in content:
        if len(next_line.split()) < 3:
            continue
        ct += 1
        toks = next_line.split(' ')
        coefs = np.asarray(toks[1:], dtype='float32')
        word_index[toks[0]] = ct
        embedding_matrix[ct] = coefs
    return embd_dim, word_index, embedding_matrix


def load_embeddings(my_args):
    print 'load_embeddings() Loading Embeddings from - ' + my_args.word_embedding
    word_index, ct = get_imp_words(my_args)
    word_count, embd_dim, word_index, ct = word_count_n_dim(my_args, word_index, ct)
    embedding_matrix = np.zeros((ct + 1, embd_dim))
    print 'embedding_matrix.shape = ' + str(embedding_matrix.shape)
    print 'len(word_index) = ' + str(len(word_index))
    print 'ct = ' + str(ct)
    lctr = 0
    with open(my_args.word_embedding) as f:
        content = f.readlines()
    for next_line in content:
        if len(next_line.split()) < 3:
            continue
        lctr += 1
        toks = next_line.split(' ')
        coefs = np.asarray(toks[1:], dtype='float32')
        embedding_matrix[word_index[toks[0]]] = coefs
        bas_utils.print_status(' / ' + str(word_count) + ' load_embeddings()         ', lctr, 1)
    rel_embd_mat = get_rel_embd_mat(my_args, embedding_matrix, word_index)
    print '\nExiting - load_embeddings()'
    return embd_dim, word_index, embedding_matrix, rel_embd_mat


def get_imp_words(args):
    ct = 0
    word_index = dict()
    imp_word_file = os.path.join(args.p['dp_home'], 'wip-data/imp_words.txt')
    ct += 1
    word_index['None'] = ct
    if not os.path.isfile(imp_word_file):
        return word_index, ct
    with open(os.path.join(args.p['dp_home'], 'wip-data/imp_words.txt')) as f:
        content = f.readlines()
    for next_line in content:
        w = next_line.replace('\n', '')
        if w not in word_index.keys():
            ct += 1
            word_index[w] = ct
    return word_index, ct


def word_count_n_dim(args, wi, ct):
    word_count, embd_dim = 0, 0
    f = open(args.word_embedding)
    for a_line in f:
        toks = a_line.split(' ')
        if len(toks) < 3:
            continue
        word_count += 1
        if embd_dim == 0:
            embd_dim = len(toks) - 1
        if toks[0] in wi.keys():
            continue
        ct += 1
        wi[toks[0]] = ct
        bas_utils.print_status(' word_count_n_dim()             ', ct, 1)
    f.close()
    word_count += 1      # Including 'None' as a new word.
    print('\nFound %s word vectors.' % word_count)
    print('Embed Mat Size - %s ' % ct)
    return word_count, embd_dim, wi, ct


def pre_process_inputs(my_args, x_all, word_index, max_sen_len, args, json_objs, qs):
    '''
    it puts the final question in 'fq' field of the json objection.
    it also prepares padded sequences of word indexes for every question
    '''
    op_path = os.path.abspath(os.path.join(args.job_folder, os.pardir, 'saved_data'))
    x_all_padded, f = list(), None
    pad_seqs_of_indexes = None
    for i in range(0, len(x_all)):
        print '\npre_process_inputs - Dataset = ' + str(i)
        seqs_of_indexes, ct, my_json_obj = list(), 0, json_objs[i]
        oov_file = open(os.path.join(op_path, 'oov-' + str(i) + '.txt'), 'w')
        for j in range(len(x_all[i])):
            qid = qs[i][j]
            qjson = my_json_obj[qid]
            q, qjson['OOV'] = x_all[i][j], ''
            sq = list()
            fq = q
            qjson['fq'] = fq
            ct += 1
            for wi in fq.split():
                if check_replace_src_ent(my_args, wi):
                    w = 'SRC_ENT'
                    qjson['fq'] = fq.replace(wi, w)
                else:
                    w = wi
                if not(w in word_index.keys()):
                    qjson['OOV'] += w + ';'
                    sq.append(0)
                    oov_file.write(qs[i][j] + ',' + qjson['qid'] + ',' + qjson['qm'] + ',' + fq + ',' + w + '\n')
                else:
                    if word_index[w] > 5432:
                        f = create_imp_words_list(str(w), f)
                    sq.append(word_index[w])
            seqs_of_indexes.append(sq)
            bas_utils.print_status(' / ' + str(len(x_all[i])) + ' pre_process_inputs()     ', j, 1)
        oov_file.close()
        pad_seqs_of_indexes = pad_sequences(seqs_of_indexes, maxlen=max_sen_len)
        x_all_padded.append(pad_seqs_of_indexes)
    f.close()
    print('Shape of pad_seqs_of_indexes tensor:', pad_seqs_of_indexes.shape)
    return x_all_padded, json_objs


def create_imp_words_list(w, f):
    if f is None:
        opf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data-3/imp_words.txt.new'
        f = open(opf, 'w')
    f.write(w + '\n')
    return f


def check_replace_src_ent(my_args, w='exxx'):
    if my_args.p['use_ere'] == 1:
        return False
    if not w.startswith('e'):
        return False
    ent_num = w[1:]
    sint = bas_utils.ignore_exception(ValueError)(int)
    en = sint(ent_num)
    if en is None:
        return False
    else:
        return True


def pre_process_relations(word_index, isl):
    '''
    Used for learning a representation of the relations using their tokens
    '''
    ctr, max_sen_len = 0, 0
    pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/input_data/split-3/rel-map-subg1.rdf'
    lc = bas_utils.get_line_count(pf)
    sqs, y, oov = list(), list(), list()
    with open(pf) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split(';')
        relid = toks[1].replace('\n', '')
        sq = list()
        max_sen_len = max(max_sen_len, len(toks[0].split()))
        for w in toks[0].split():
            if not (w in word_index.keys()):
                sq.append(0)
            else:
                sq.append(word_index[w])
        sqs.append(sq)
        y.append(relid)
        ctr += 1
        bas_utils.print_status(' / ' + str(lc) + ' pre_process_relations()                   ', ctr, 1)
    pad_seqs_of_indexes = pad_sequences(sqs, maxlen=isl)
    print '\nrelation token - seq len = ' + str(max_sen_len)
    print pad_seqs_of_indexes[0]
    print '\nExiting - pre_process_relations()'
    return pad_seqs_of_indexes, y


def pre_process_outputs(args, y_all, word_index, embedding_matrix, rmat, max_op_length, isl):
    print 'Shape of y_all_new, i.e., Training, Validation, and Test ..., osl=' + str(max_op_length)
    y_all_new = []
    for y_dataset in y_all:
        y_dataset_new = []
        for rel_seq in y_dataset:
            y_query = []
            for r in rel_seq:
                e = rmat[r]
                y_query.append(e)
            while len(y_query) != max_op_length:
                y_query.append(np.zeros(y_query[0].shape, dtype=float))
            y_dataset_new.append(y_query)
        np_y_dataset = np.asarray(y_dataset_new, dtype=float)
        print 'np_y_dataset.shape=' + str(np_y_dataset.shape)
        y_all_new.append(np_y_dataset)
    print '======================================================================================================'
    print y_all_new[0].shape
    print '======================================================================================================'
    return y_all_new


def get_rel_embd_mat(my_args, embedding_mat, word_idx):
    rel_embd_mat = dict()
    sint = bas_utils.ignore_exception(ValueError)(int)
    for w in word_idx.keys():
        if not str(w).startswith('r') or sint(w[1:]) is None:
            continue
        ind = word_idx[w]
        e1 = embedding_mat[ind]
        e = e1
        rel_embd_mat[w] = e
    return rel_embd_mat

