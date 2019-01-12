from keras import callbacks
from keras.utils import plot_model
import load_prepare_data
import run_model_eval
from keras import backend as ke
import os
import sys
import utils.basics as bas_utils
import mods.bidi_lstm_s2s as bidi_s2s
from shutil import copyfile



lfn = None
cos_sim, tf_sess, a, b = None, None, None, None
job_name = 'job-1'
load_legend = ['load from saved_data', 'save to saved_data', 'pre-process, but don\'t save or load']
p = dict()


def check_input_arguments():
    if len(sys.argv) < 2:
        sys.stderr.write('Error: Not enough arguments. \n')
        sys.stderr.write('Help: Set all parameters in kgt.conf, and provide its path-name as argument.\n')
        sys.stderr.write(sys.argv[0] + ' <path>/kgt.conf\n')
        sys.exit()
    conf_path_file = sys.argv[1]
    return conf_path_file


def parse_params(conf_pf):
    global p
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
    lod_home = os.environ['WORK_DIR']
    p['dp_home'] = os.path.join(lod_home, p['dp_name'])
    my_args = MyArgs(p)
    jf, jn = set_job_folder(os.path.join(p['dp_home'], 'model/kgrep'))
    p['job_folder'] = jf
    p['job_number'] = jn
    p['conf_file'] = conf_pf
    my_args.job_folder = jf
    copyfile(conf_pf, os.path.join(p['job_folder'], os.path.basename(conf_pf)))
    print '========================================================='
    return my_args


def set_job_folder(base_folder='/data/Work-Homes/LOD_HOME/fb15k2/model/kgrep/'):
    max_ct = 0
    for next_file in os.listdir(base_folder):
        if next_file.startswith('job-'):
            next_ct = int(next_file.replace('job-', ''))
            max_ct = max(max_ct, next_ct)
    job_number = int(max_ct+1)
    tb_log_folder = os.path.join(base_folder, 'job-' + str(job_number))
    print 'tb_log_folder=' + tb_log_folder
    os.mkdir(tb_log_folder)
    return tb_log_folder, job_number


class MyArgs:
    def __init__(self, ip):
        self.p = ip
        self.edge_list_pf = os.path.join(p['dp_home'], 'kg/converted-rdf-' + p['dp_name'] + '.rdf')
        self.job_folder = '/data/DATA_HOME/fb15k/model/kgrep/try/'
        self.word_embedding = os.path.join(ip['dp_home'], ip['embedding_suffix'])
        self.input_path = os.path.join(ip['dp_home'], ip['input_suffix'])


def main(conf_file):
    my_args = parse_params(conf_file)
    em_dim, word_ind, em_mat, rmat, isl, x_all, np_y_all, y_all, src_ent_all, osl, jos, qs, \
    rel_tok_seqs, rel_ids = load_prepare_data.main(my_args)
    print_basics(em_dim, len(word_ind), len(em_mat), isl, osl)
    if p['load_command'] == 1:
        return
    x_train, y_train, x_valid, y_valid = x_all[0], np_y_all[0], x_all[1], np_y_all[1]
    print 'x_train.shape=' + str(x_train.shape)
    print 'isl=' + str(isl)
    store_settings(my_args)
    preds_trn, preds_tst, learned_emat, ygt = run_model(my_args, em_mat, rmat, word_ind, em_dim, isl, osl, x_train, y_train,
                                                        x_valid, y_valid, x_all[2], rel_tok_seqs, rel_ids, y_all,
                                                        src_ent_all, jos, qs)
    print '\ntb_log_folder=' + str(my_args.job_folder)
    save_predictions(my_args, preds_tst, 'tst')
    run_model_eval.check_accuracy(my_args, preds_tst, y_all[2], src_ent_all[2], word_ind, learned_emat, rmat,
                                  osl, jos[2], qs[2], split_name='tst')


def run_model(args, em_mat, rel_mat, word_ind, em_dim, isl, osl, x_train, y_train, x_valid, y_valid, x_test,
              rel_tok_seqs, rel_ids, y_all, src_ent_all, jos, qs):
    my_mod, to_fp = bidi_s2s.get_model3(p, em_mat, rel_mat, word_ind, em_dim, isl, osl)
    my_predictions_trn, my_predictions_tst, emat, ygt = fit_and_predict(args, my_mod, x_train, y_train, x_valid, y_valid, x_test)
    return my_predictions_trn, my_predictions_tst, emat, ygt


def fit_and_predict(my_args, my_model, x_train, y_train, x_valid, y_valid, x_test):
    plot_model(my_model, to_file=os.path.join(my_args.job_folder, 'model-' + str(p['job_number']) + '.png'))
    tb = callbacks.TensorBoard(log_dir=my_args.job_folder, histogram_freq=0, batch_size=32, write_graph=False,
                               write_grads=True, write_images=False, embeddings_freq=0,
                               embeddings_layer_names=None, embeddings_metadata=None)
    fp = my_args.job_folder + '/weights.{epoch:02d}-{val_loss:.4f}.hdf5'
    mc = callbacks.ModelCheckpoint(filepath=fp, save_best_only=True, mode='auto')
    print 'Starting to fit the model ...'
    if 'weight_file' in p.keys():
        fn = os.path.join(p['job_folder'], p['weight_file'])
        my_model.load_weights(fn)
    elif len(x_valid) < 5:
        my_model.fit(x=x_train, y=y_train, epochs=p['epoch_count'], verbose=1, callbacks=[tb,mc])
    else:
        print 'Length of x_valid arrary = ' + str(len(x_valid))
        print 'y_train.shape=' + str(y_train.shape)
        print 'y_valid.shape=' + str(y_valid.shape)
        my_model.fit(x=x_train, y=y_train, validation_data=(x_valid, y_valid), epochs=p['epoch_count'], verbose=1,
                     callbacks=[tb, mc])
    my_model.save(my_args.job_folder + '/final.model.h5')
    my_model.save_weights(my_args.job_folder + '/final.model.weights.h5')
    print 'Starting to predict using the model ... with Tst Data First'
    my_predictions_tst = my_model.predict(x=x_test, verbose=1)
    print '\nmy_predictions_tst.shape=' + str(my_predictions_tst.shape)
    print 'my_predictions_tst[0].shape=' + str(my_predictions_tst[0].shape)
    print 'my_predictions_tst[1].shape=' + str(my_predictions_tst[1].shape)
    my_predictions_trn = my_predictions_tst # temporarily disabling this
    tst_pres = my_predictions_tst
    trn_pres = my_predictions_trn
    return trn_pres, tst_pres, my_model.layers[1].get_weights()[0], None


def save_predictions(my_args, np_y_all_pred, split_name):
    print 'Entering save_predictions() - for ' + split_name
    print 'len(np_y_all_pred)=' + str(len(np_y_all_pred))
    print 'np_y_all_pred.shape=' + str(np_y_all_pred.shape)
    op_file = bas_utils.open_file(os.path.join(my_args.job_folder, split_name + '_pred_embeddings.txt'))
    for i in range(len(np_y_all_pred)):
        next_pred_list = np_y_all_pred[i]
        for pred_e in next_pred_list:
            op_file.write(bas_utils.to_string(pred_e, ',') + ';')
        op_file.write('\n')
    op_file.close()
    print 'Exiting save_predictions() - for ' + split_name


def myloss(y_true, y_pred):
    v1 = y_pred
    v2 = y_true
    numerator = ke.sum(v1 * v2)
    denominator = ke.sqrt(ke.sum(v1 ** 2) * ke.sum(v2 ** 2))
    loss = abs(1 - numerator/denominator)
    return loss


def print_basics(em_dim, len_word_ind, len_em_mat, isl, osl):
    print '--------------------------------------------------------------------------'
    print 'em_dim=' + str(em_dim)
    print 'len_word_ind=' + str(len_word_ind)
    print 'len_em_mat=' + str(len_em_mat)
    print 'Input Sequence Length=' + str(isl)
    print 'Output Sequence Length=' + str(osl)
    print '--------------------------------------------------------------------------'
    print '                              Loaded data '
    print '--------------------------------------------------------------------------'


def store_settings(args):
    op_file = open(os.path.join(args.job_folder, 'params.txt'), 'w')
    for k in p.keys():
        op_file.write(k+'=' + str(p[k]) + '\n')
    op_file.close()


if __name__ == '__main__':
    pf = check_input_arguments()
    main(pf)
