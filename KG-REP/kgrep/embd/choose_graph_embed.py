import os
import sys
import numpy as np
from utils import basics as bas_utils
import utils.my_map as mm

eid_list_pf, rel_map_pf, node_map_pf = '', '', ''
dp_home, trn_file, val_file, tst_file, rel_tok_file, oov_pf, output_pf, all_q_file = '', '', '', '', '', '', '', ''
random_embedding_file, ere_embedding_file, question_key = '', '', ''


def check_input_arguments():
    if len(sys.argv) < 5:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <dp_name> <node-map-file> <rel-map-file> <ere-embedding-file-suffix>\n')
        sys.stderr.write('The node map, and rel map files, should be in WORK_DIR/$dp_name/kg/\n')
        sys.stderr.write('The EID list file should contain the list of entity ids used in the data\n')
        sys.stderr.write('\nExample:\n')
        webqsp_msg = 'node-map-freebase_subgraph.rdf rel-map-freebase_subgraph-manual.rdf'
        webqsp_msg = webqsp_msg + ' model/ere/w2v-300-10-5-1-100.txt\n'
        sys.stderr.write('python ' + sys.argv[0] + ' webqsp ' + webqsp_msg)
        sys.stderr.write('python ' + sys.argv[0] + ' This step not required for fb15k dataset\n')
        sys.exit(1)
    global dp_home, output_pf, random_embedding_file, ere_embedding_file, rel_map_pf, node_map_pf, eid_list_pf
    global ere_embedding_file
    dp_name = sys.argv[1]
    print 'dp_name=', dp_name
    dp_home = os.path.join(os.environ['WORK_DIR'], dp_name)
    print 'dp_home=', dp_home
    print '============================================================================='
    eid_list_pf = os.path.join(dp_home, 'input_data', 'eid-list.txt')
    print 'Entity-ID List File = ' + eid_list_pf
    node_map_pf = os.path.join(dp_home, 'kg', sys.argv[2])
    print 'Node Map File = ' + node_map_pf
    rel_map_pf = os.path.join(dp_home, 'kg', sys.argv[3])
    print 'Relationship Map File = ' + rel_map_pf
    random_embedding_file = os.path.join(dp_home, 'model/ere-glove/re.txt')
    print 'Using random embedding file = ' + random_embedding_file
    ere_embedding_file = os.path.join(dp_home, sys.argv[4])
    print 'Using ere embedding file = ' + ere_embedding_file
    fn = os.path.basename(ere_embedding_file)
    output_pf = os.path.join(dp_home, 'model/ere-glove/aug-' + fn )
    print 'Output will be stored in file= ' + output_pf
    print '============================================================================='


def main():
    nm = load_node_map()
    src_ent_wi = get_source_ents(nm)
    word_index = load_rel_ids(src_ent_wi)
    print '\ntotal input word count = ' + str(len(word_index))
    re = get_random_embddings()
    em = get_ere_embed(word_index, re)
    print '\nEmbeddings Obtained, starting to write...'
    write_embd(word_index, em)


def get_source_ents(nm):
    print '\nEntering - get_source_ents() for - ' + eid_list_pf
    word_index, ct = dict(), 0
    word_index['NONE'] = 0
    with open(eid_list_pf) as f:
        content = f.readlines()
    for next_line in content:
        nl = next_line.replace('\n', '')
        toks = nl.split(',')
        eid = nm.get(toks[0])
        if eid in word_index.keys():
            continue
        ct += 1
        word_index[eid] = ct
    print '\nExiting - get_source_ents() len(word_index.keys())= ' + str(len(word_index.keys())) + ', ct=' + str(ct)
    return word_index


def load_rel_ids(word_index):
    inittial_ct = len(word_index)
    with open(rel_map_pf) as f:
        content = f.readlines()
    for next_line in content:
        ln = next_line.replace('\n', '')
        toks = ln.split()
        if toks[1] in word_index.keys():
            print 'Duplicate Rel - ' + toks[1]
            continue
        idx = len(word_index)
        word_index[toks[1]] = idx
    print 'Exiting - load_rel_ids - len(word_index)=' + str(len(word_index.keys())) + \
          ', Net Addition=' + str(len(word_index.keys()) - inittial_ct)
    return word_index


def get_random_embddings():
    emb = list()
    with open(random_embedding_file) as f:
        content = f.readlines()
    for next_line in content:
        e = next_line.split(',')
        emb.append(e)
    return emb


def get_ere_embed(wi, random_embeddings):
    print '\nEntering get_ere_embed() - len(wi)=' + str(len(wi.keys()))
    ct, i, idx, word_list = 0, 0, 0, set(wi.keys())
    embedding_matrix = np.zeros((len(wi) + 1, 300))
    with open(ere_embedding_file) as f:
        content = f.readlines()
    for next_line in content:
        i += 1
        msg = 'i=' + str(i) + ', idx=' + str(idx) + ' / ' + str(len(wi))
        bas_utils.print_status(msg + '  get_ere_embed()', ct, 1)
        my_words = wi.keys()
        toks = next_line.split()
        if len(toks) < 5:
            continue
        if toks[0] not in my_words:
            continue
        word_list.remove(toks[0])
        ct += 1
        idx = wi[toks[0]]
        embedding_matrix[idx] = np.asarray(toks[1:], dtype=float)
    print '\nWord count not in ERE=' + str(len(word_list)) + ', e.g., ' + list(word_list)[0] + ', ' + list(word_list)[1]
    print '\n - Starting to add Random Embedding after ct=' + str(ct)
    final_pending = set(word_list)
    for w in word_list:
        if not str(w).startswith('r'):
            continue
        print 'Adding Random Embedding for - ' + w
        idx = wi[w]
        e = random_embeddings.pop()
        embedding_matrix[idx] = np.asarray(e, dtype=float)
        ct += 1
        final_pending.remove(w)
    print '\nWord count not in final_embd=' + str(len(final_pending)) + ' - ' + bas_utils.to_string(final_pending, ' ')
    print '\nct=' + str(ct) + ', i=' + str(i)
    return embedding_matrix


def is_rel_id(word):
    sint = bas_utils.ignore_exception(ValueError)(int)
    is_rel = False
    if str(word).startswith('r'):
        id = sint(word[1:])
        if id is not None:
            is_rel = True
    return is_rel


def write_embd(wi, e_mat):
    op_file = open(output_pf, 'w')
    my_words = wi.keys()
    for w in my_words:
        idx = wi[w]
        e = e_mat[idx]
        next_line = w + ' ' + bas_utils.to_string(my_list=e, separator=' ') + '\n'
        op_file.write(next_line)
    print '\nNew Embedding file written to - ' + output_pf
    op_file.close()


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


if __name__ == '__main__':
    check_input_arguments()
    main()
