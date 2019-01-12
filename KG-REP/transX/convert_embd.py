import os
import numpy as np
from utils import basics as bas_utils


transx_output_folder = '/data/paper-codes/Fast-TransX-master/output/transR/FB15K/'
transx_input_folder = '/data/paper-codes/Fast-TransX-master/data/FB15K/'

my_rel_map = '/data/Work-Homes/LOD_HOME/fb15k2/wip-data-3/rel-map-fb15k.txt'
my_ent_map = '/data/Work-Homes/LOD_HOME/fb15k2/wip-data-3/node-map-fb15k.txt'

output_file = transx_output_folder + '/main.transr.embd'


def load_embedding(file_name, emat):
    with open(file_name) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split()
        emat.append(np.asarray(toks, dtype=float))
    return emat


def load_transx_word_index(file_name, word_index):
    with open(file_name) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split()
        if len(toks) < 2:
            continue
        w = toks[0]
        id = toks[1]
        word_index[w] = id
    return word_index


def load_my_word_index(fn, word_index):
    with open(fn) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split()
        if len(toks) < 2:
            continue
        w = toks[0]
        id = toks[1]
        word_index[w] = id
    return word_index


def convert_indentifier(tx_wi, my_wi, emat):
    embd_dict = dict()
    for w in tx_wi.keys():
        tx_id = tx_wi[w]
        my_id = my_wi[w]
        e = emat[int(tx_id)]
        embd_dict[my_id] = e
    return embd_dict


def write_embd(e_mat, my_mode):
    op_file = open(output_file, my_mode)
    my_words = e_mat.keys()
    for w in my_words:
        next_line = w + ' ' + bas_utils.to_string(e_mat[w]) + '\n'
        op_file.write(next_line)
    op_file.close()


def main():
    entity_embd_pf = os.path.join(transx_output_folder, 'entity2vec.vec')
    entity_wi_pf = os.path.join(transx_input_folder, 'entity2id.txt')
    ent_e_mat = load_embedding(entity_embd_pf, list())
    txwi = load_transx_word_index(entity_wi_pf, dict())
    mywi = load_my_word_index(my_ent_map, dict())
    ent_mat_map = convert_indentifier(txwi, mywi, ent_e_mat)
    write_embd(ent_mat_map, 'w')
    # Now Relations
    relation_embd_pf = os.path.join(transx_output_folder, 'relation2vec.vec')
    relation_wi_pf = os.path.join(transx_input_folder, 'relation2id.txt')
    rel_e_mat = load_embedding(relation_embd_pf, list())
    txwi = load_transx_word_index(relation_wi_pf, dict())
    mywi = load_my_word_index(my_rel_map, dict())
    ent_mat_map = convert_indentifier(txwi, mywi, rel_e_mat)
    write_embd(ent_mat_map, 'a')


if __name__ == '__main__':
    main()