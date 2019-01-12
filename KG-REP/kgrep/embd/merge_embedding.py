import os
import sys
from utils import basics as bas_utils

base_folder = ''


def check_input_arguments():
    if len(sys.argv) < 3:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <dp_name> <embedding_file_1> <embedding_file_2>\n')
        sys.stderr.write('Above filenames should given with respect to relative to base_folder')
        sys.stderr.write('base_folder = WORK_DIR/$dp_name/model/ere-glove/')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python ' + sys.argv[0]+' fb15k w2v-300-10-10-1-10.txt glove.txt\n')
        sys.stderr.write('python ' + sys.argv[0] + ' webqsp aug-w2v-300-10-10-1-10.txt glove.txt\n')
        sys.exit(1)
    global base_folder
    dp_name = sys.argv[1]
    base_folder = os.path.join(os.environ['WORK_DIR'], dp_name, 'model/ere-glove/')
    pf1 = os.path.join(base_folder, sys.argv[2])
    pf2 = os.path.join(base_folder, sys.argv[3])
    opf = os.path.join(base_folder, 'merged.txt')
    return pf1, pf2, opf


def load_embd(file_name):
    embd_map = dict()
    with open(file_name) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split()
        if len(toks) < 5:
            continue
        embd_map[toks[0]] = toks[1:]
    print 'loaded - ' + str(len(embd_map)) + ' embeddings...'
    return embd_map


def merge_embeddings(pf1, pf2, opf):
    print 'Loading - ' + pf1
    e1 = load_embd(pf1)
    print 'Loading - ' + pf2
    e2 = load_embd(pf2)
    print 'Merging embeddings ...'
    for w in e2.keys():
        e1[w] = e2[w]
    print 'merged embedding size - ' + str(len(e1))
    print 'Printing embeddings ...' + opf
    print_embd(e1, opf)


def print_embd(merged_embd, opf):
    op_file = open(opf, 'w')
    for w in merged_embd.keys():
        op_file.write(w + ' ' + bas_utils.to_string(merged_embd[w], ' ') + '\n')
    op_file.close()


if __name__ == '__main__':
    pf1, pf2, opf = check_input_arguments()
    merge_embeddings(pf1, pf2, opf)
