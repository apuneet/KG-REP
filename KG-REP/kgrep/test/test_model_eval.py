import kgrep.load_prepare_data
import kgrep.run_model_eval
import os
import numpy as np
from utils import basics as bas_utils


test_fraction = 1


class MyArgsWebQsp:
    def __init__(self):
        self.p = {}
        self.edge_list_pf = ''
        self.job_folder  = '/data/Work-Homes/LOD_HOME/subgraph_webq/model/kgrep/try-job'
        #self.job_folder = '/data/Work-Homes/LOD_HOME/subgraph_webq/model/kgrep-colab/job-1'
        #self.job_folder = '/data/Work-Homes/LOD_HOME/fb15k2/model/kgrep/try-job'
        #self.word_embedding = 'model/allq_ere/m.embd'
        self.input_path = ''
        self.load_command = 0

    def set_details(self, ip):
        self.p = ip
        self.edge_list_pf = os.path.join(ip['dp_home'], 'wip-data-3/converted-rdf-' + ip['dp_name'] + '.rdf')
        self.word_embedding = os.path.join(ip['dp_home'], ip['embedding_suffix'])
        self.input_path = os.path.join(ip['dp_home'], ip['input_suffix'])


def parse_params():
    my_args = MyArgsWebQsp()
    p = dict()
    conf_pf = os.path.join(my_args.job_folder, 'kgt.conf')
    sint = bas_utils.ignore_exception(ValueError)(int)
    sfloat = bas_utils.ignore_exception(ValueError)(float)
    with open(conf_pf) as f:
        content = f.readlines()
    for next_line in content:
        if next_line.startswith('#') or next_line == '\n' or len(next_line) == 0:
            continue
        toks = next_line.split('=')
        val = toks[1].replace('\n', '')
        print toks[0] + '=' + str(val)
        if sint(val) is not None:
            p[toks[0]] = sint(val)
            continue
        if sfloat(val) is not None:
            p[toks[0]] = sfloat(val)
            continue
        p[toks[0]] = val
    lod_home = os.environ['LOD_HOME']
    p['dp_home'] = os.path.join(lod_home, p['dp_name'])
    p['job_folder'] = my_args.job_folder
    p['job_number'] = os.path.basename(my_args.job_folder)
    my_args.set_details(p)
    print '========================================================='
    return my_args


def main():
    my_args = parse_params()
    #embd_dim, word_index, embed_mat, isl, x_all, np_y_all, y_all, src_ent_all, osl, jos, qs = kgrep.load_prepare_data.main(my_args)
    embd_dim, word_index, embed_mat, rel_mat, max_sen_len, x_all_padded, np_y_all, y_all, src_ent_all, osl, jos, \
    qs, rel_tok_seqs, rel_ids = kgrep.load_prepare_data.main(my_args)
    max_ct = int(len(np_y_all[2]) * test_fraction)
    job_id = os.path.basename(my_args.job_folder)
    if job_id == 'try-job':
        kgrep.run_model_eval.check_accuracy(my_args, np_y_all_pred=np_y_all[2][:max_ct], y_all_true=y_all[2][:max_ct],
                                            src_ents=src_ent_all[2][:max_ct], word_index=word_index,
                                            embed_mat=embed_mat, rmat=rel_mat, op_seq_len=osl,
                                            json_obj=jos[2], qid_seq=qs[2])
    else:
        my_pred = read_predictions(my_args)
        kgrep.run_model_eval.check_accuracy(my_args, np_y_all_pred=my_pred, y_all_true=y_all[2],
                                            src_ents=src_ent_all[2], word_index=word_index, embed_mat=embed_mat,
                                            rmat=rel_mat, op_seq_len=osl, json_obj=jos[2], qid_seq=qs[2])
    print '.................... Done'


def read_predictions(my_args):
    all_pred = list()
    with open(os.path.join(my_args.job_folder, 'tst_pred_embeddings.txt')) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split(';')
        p1 = np.asarray(toks[0].split(','), dtype=np.float32)
        p2 = np.asarray(toks[1].split(','), dtype=np.float32)
        next_pred = list()
        next_pred.append(p1)
        next_pred.append(p2)
        all_pred.append(next_pred)
    np_all_pred = np.asarray(all_pred, dtype=np.float32)
    return np_all_pred



if __name__ == '__main__':
    main()