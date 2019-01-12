import os
import networkx as nx
import tensorflow as tf
import utils.basics as bas_utils
import kgrep.test.test_model_eval


cos_sim, tf_sess,  a, b = None, None, None, None
nbr_ent_cache = None
nbr_rel_cache = None


def check_accuracy(my_args, np_y_all_pred, y_all_true, src_ents, word_index, embed_mat, rmat, op_seq_len, json_obj,
                   qid_seq, split_name='tst'):
    '''
    :param my_args:
    :param np_y_all_pred:   -   numpy, list of predicted sequence of embeddings for every question
    :param y_all_true:      -   sequence of relation-ids, for every question, therefore list of lists
    :param src_ents:        -   list source entities. It is a list of list. On list for every question in order.
    :param word_index:      -   dictionary, key=word, value=row_number in embed_mat(int)
    :param embed_mat:       -   Embedding Matrix
    :param op_seq_len:      -   Output Sequence Length
    :param json_obj:        -   JSON Object of the input test data
    :param qid_seq:         -   Sequence of Question-IDs
    :param split_name:      -   Name of the Split taken from $DP_HOME/input_data folder
    :return:
    '''
    print '\n --->check_accuracy()<--- for ' + split_name
    all_rel_ids = get_all_relids(word_index)
    neg_data = list()
    beam_size_given = my_args.p['beam_size']
    if isinstance(beam_size_given, int):
        toks = [beam_size_given]
    else:
        toks = beam_size_given.split(':')
    if split_name == 'trn':
        toks = [toks[len(toks)-1]]
    for nxt_beam_size in toks:
        print 'Calling eval_model for nxt_beam_size=' + str(nxt_beam_size)
        my_args.p['beam_size'] = int(nxt_beam_size)
        neg_data = eval_model(my_args, np_y_all_pred, y_all_true, src_ents, word_index, embed_mat, rmat, op_seq_len,
                              json_obj, qid_seq, all_rel_ids, split_name)
    return neg_data


def eval_model(my_args, np_y_all_pred, y_all_true, src_ents, word_index, embed_mat, rmat, op_seq_len, json_obj,
                   qid_seq, all_rel_ids, split_name='tst'):
    print '\nEntering - eval_model()<--- for ' + split_name + ', beam_size=' + str(my_args.p['beam_size'])
    print 'np_y_all_pred.shape=' + str(np_y_all_pred.shape)
    print 'Reading Edge List in networkx ... from ' + my_args.edge_list_pf + '\n'
    g = nx.read_edgelist(my_args.edge_list_pf, nodetype=str, data=(('relation', str),), create_using=nx.DiGraph())
    r, results, gt_lengths, neg_data = '', [], [], dict()
    op_file = bas_utils.open_file(os.path.join(my_args.job_folder, split_name + '_pred_distances.txt'))
    ct = 0
    for i in range(len(src_ents)):          # for every question
        ct += 1
        y_pred, y_true, my_ents = np_y_all_pred[i], y_all_true[i], src_ents[i]
        qid = qid_seq[i]
        jsonq = json_obj[qid]
        is_true, jq1, neg_data = eval_next_xy(my_args, g, qid, y_pred, y_true, my_ents, word_index, embed_mat, rmat,
                                              jsonq, i, op_file, neg_data, all_rel_ids, split_name)
        json_obj[qid] = jq1
        results.append(is_true)
        gt_lengths.append(len(y_true))
        bas_utils.print_status(' / ' + str(len(src_ents)) + ' check_accuracy()             ', i, 1)
    op_file.close()
    save_neg_data(my_args, neg_data, split_name)
    cum_seq_right, ind_seq_right, all_right, json2 = cal_stats(my_args, results, gt_lengths, op_seq_len, json_obj,
                                                               qid_seq, split_name)
    print_results(my_args, cum_seq_right, ind_seq_right, all_right, results, split_name)
    bas_utils.save_json_to_file(json2, os.path.join(my_args.job_folder, split_name + '_res.json'), True)
    sd_folder = os.path.abspath(os.path.join(my_args.job_folder, os.pardir, 'saved_data'))
    bas_utils.save_json_to_file(nbr_ent_cache, os.path.join(sd_folder, 'nbr_ent_cache.json'))
    bas_utils.save_json_to_file(nbr_ent_cache, os.path.join(sd_folder, 'nbr_rel_cache.json'))
    return neg_data


def save_neg_data(my_args, neg_data, split_name):
    neg_data_pf = os.path.join(my_args.job_folder, split_name + '_neg_data.json')
    bas_utils.save_json_to_file(neg_data, neg_data_pf)


def eval_next_xy(my_args, g, qid, y_pred, y_true, my_ents, word_ind, emb_mat, rmat, q_json, qno, op_file, neg_data,
                 all_rel_ids, split_name):
    if my_args.p['dp_name'] == 'fb15k':
        is_true, q_json, neg_data = eval_next_xy_4(my_args, g, qid, y_pred, y_true, my_ents, word_ind, emb_mat, rmat,
                                                   q_json, qno, op_file, neg_data, all_rel_ids, split_name)
    else:
        is_true, q_json, neg_data = eval_next_xy_2(my_args, g, qid, y_pred, y_true, my_ents, word_ind, emb_mat, rmat,
                                                   q_json, qno, op_file, neg_data, all_rel_ids, split_name)
    return is_true, q_json, neg_data


def eval_next_xy_2(my_args, g, qid, y_pred, y_true, my_ents, word_ind, emb_mat, rmat, q_json, qno, op_file, neg_data,
                 all_rel_ids, split_name):
    l1tkr, tkr, prev_beam_map, final_beam_map = list(), list(), dict(), dict()
    y_true = match_y_true(y_pred, y_true)
    for j in range(2):
        is_rel_in_kg, beam_map = False, dict()
        if j == 0:
            ent_lists_4_tkr = list()
            ent_lists_4_tkr.append(my_ents)
            tkr.append("")
            prev_beam_map[""] = 1
        else:
            ent_lists_4_tkr = get_neigbourgood_ents(my_args, g, my_ents[0], tkr, all_rel_ids)
        for l in range(0, len(ent_lists_4_tkr), 1):
            nxt_rel = tkr[l]
            nxt_rel_dist = prev_beam_map[nxt_rel]
            ent_list_4_nxt_rel = ent_lists_4_tkr[l]
            for ent in ent_list_4_nxt_rel:
                if ent == '_MYENTMENTION_':
                    beam_map, ent_has_true_rel = add_all_to_beam_map(my_args, all_rel_ids, word_ind, emb_mat, rmat,
                                                                     y_pred[j], y_true[j], nxt_rel_dist, nxt_rel,
                                                                     beam_map)
                else:
                    beam_map, ent_has_true_rel = get_neigbourgood_rels(my_args, g, ent, beam_map, y_pred[j], y_true[j],
                                                                       nxt_rel_dist, nxt_rel, word_ind, emb_mat, rmat)
                if ent_has_true_rel:
                    is_rel_in_kg = True
        if len(ent_lists_4_tkr) == 0 or len(beam_map) == 0:
            beam_map = attach_None(prev_beam_map)
        tkr = bas_utils.sort_map(my_map=beam_map, isDescending=True, top_k=int(my_args.p['beam_size']))
        if j == 0:
            l1tkr = tkr
            prev_beam_map = beam_map
        else:
            final_beam_map = beam_map
        if 'no_rel' not in q_json.keys():
            q_json['no_rel'] = ''
        if y_true[j] is not None and not is_rel_in_kg:
            q_json['no_rel'] += y_true[j] + ';'
    tkp = bas_utils.sort_map(my_map=final_beam_map, isDescending=True, top_k=int(my_args.p['beam_size']))
    q_json['rank'] = get_rank(tkp, y_true, q_json['qid'])
    q_json, is_true = update_json_new(q_json, y_true, tkp, final_beam_map)
    ns = set()
    if len(ns) > 3:
        print 'More than 3 Neg Pairs for QID=' + qid
    q_json['neg_seqs'] = list(ns)
    neg_data[q_json['qid']] = list(ns)
    return is_true, q_json, neg_data


def eval_next_xy_4(my_args, g, qid, y_pred, y_true, my_src_ents, word_ind, emb_mat, rmat, q_json, qno, op_file, neg_data,
                 all_rel_ids, split_name):
    """
    sorted_beam_list can also be called as top_k_relations_list

    """
    l1_sorted_beam_list, sorted_beam_list, prev_beam_map,  = list(), list(), dict()
    final_beam_map = dict()
    y_true = match_y_true(y_pred, y_true)
    for i in range(2):
        my_ents = list()
        my_ents.append(my_src_ents[i])
        if i == 0:
            sorted_beam_list.append("")
            prev_beam_map[""] = 1
        for j in range(2):
            beam_map = dict()
            ent_lists_4_tkr = get_ent_list_4_top_k_rels(my_args, g, j, my_ents, sorted_beam_list, all_rel_ids)
            beam_map, is_rel_in_kg = get_beam_map(my_args, qid, g, sorted_beam_list, ent_lists_4_tkr, beam_map,
                                                  prev_beam_map, all_rel_ids, word_ind, emb_mat, rmat, y_true[i*2 + j],
                                                  y_pred[i*2 + j])
            sorted_beam_list = bas_utils.sort_map(my_map=beam_map, isDescending=True, top_k=int(my_args.p['beam_size']))
            if i == 1 and j == 1:
                final_beam_map = beam_map
            else:
                prev_beam_map = beam_map
                # End of internal Loop
    # End of External loop
    tkp = bas_utils.sort_map(my_map=final_beam_map, isDescending=True, top_k=int(my_args.p['beam_size']))
    q_json['rank'] = get_rank(tkp, y_true, q_json['qid'])
    q_json, is_true = update_json_new(q_json, y_true, tkp, final_beam_map)
    ns = set()
    if len(ns) > 3:
        print 'More than 3 Neg Pairs for QID=' + qid
    q_json['neg_seqs'] = list(ns)
    neg_data[q_json['qid']] = list(ns)
    return is_true, q_json, neg_data


def get_ent_list_4_top_k_rels(my_args, g, j, my_ents, tkr, all_rel_ids):
    ent_lists_4_tkr = list()
    if j == 0:
        ent_lists_4_tkr.append(my_ents)
    else:
        ent_lists_4_tkr = get_neigbourgood_ents(my_args, g, my_ents[0], tkr, all_rel_ids)
    return ent_lists_4_tkr


def get_beam_map(my_args, qid, g, tkr, ent_lists_4_tkr, beam_map, prev_beam_map, all_rel_ids, word_ind, emb_mat, rmat, y_true, y_pred):
    is_rel_in_kg = False
    if ent_lists_4_tkr is None:
        print '=============       ERROR       ==================='
        print '\nqid = ' + qid
        print '=============       ERROR       ==================='
    for l in range(0, len(ent_lists_4_tkr), 1):
        nxt_rel = tkr[l]
        nxt_rel_dist = prev_beam_map[nxt_rel]
        ent_list_4_nxt_rel = ent_lists_4_tkr[l]
        for ent in ent_list_4_nxt_rel:
            if ent == '_MYENTMENTION_':
                beam_map, ent_has_true_rel = add_all_to_beam_map(my_args, all_rel_ids, word_ind, emb_mat, rmat,
                                                                 y_pred, y_true, nxt_rel_dist, nxt_rel,
                                                                 beam_map)
            else:
                beam_map, ent_has_true_rel = get_neigbourgood_rels(my_args, g, ent, beam_map, y_pred, y_true,
                                                                   nxt_rel_dist, nxt_rel, word_ind, emb_mat, rmat)
            if ent_has_true_rel:
                is_rel_in_kg = True
    if len(ent_lists_4_tkr) == 0 or len(beam_map) == 0:
        beam_map = attach_None(prev_beam_map)
    return beam_map, is_rel_in_kg


def get_rank(beam_map, y_ground_truth, qid):
    gt1 = y_ground_truth[0]
    gt2 = y_ground_truth[1]
    ct, rank = 0, -1
    for nxt_pred in beam_map:
        toks = nxt_pred.split(',')
        if len(toks) < 2:
            print 'nxt_pred = ' + nxt_pred + ', qid=' + qid
        p1 = toks[0]
        p2 = toks[1]
        if p1 == gt1 and p2 == gt2:
            rank = ct
            break
        ct += 1
    return rank


def attach_None(prev_beam_map):
    beam_map = dict()
    for next_path in prev_beam_map.keys():
        new_next_path = next_path + ',None'
        beam_map[new_next_path] = prev_beam_map[next_path]
    return beam_map


def match_y_true(y_pred, y_true):
    """
    This function is used for making the length of the sequence y_true equal to the length of the sequence y_pred.
    This is needed because predicted seq length is always max_osl but sometimes actual sequence length is smaller.
    """
    osl = len(y_pred)
    while len(y_true) < osl:
        y_true.append('None')
    return y_true


def update_json_new(q_json, y_true, top_k_rels, my_beam_map):
    is_true = [False] * len(y_true)
    pred_rid_seq = list()
    if len(top_k_rels) == 0:
        print 'TKP Null - in update_json_new - ' + q_json['qid']
    pred_rel_seq = top_k_rels[0].split(',')
    for i in range(0, len(pred_rel_seq), 1):
        predicted_rel = pred_rel_seq[i]
        y_true_next = y_true[i]
        pred_rid_seq.append(predicted_rel)
        if y_true_next is not None:
            is_true[i] = True if predicted_rel == y_true_next else False
        else:
            is_true[i] = True if predicted_rel == 'None' else False
    q_json['pred_rid_seq'] = pred_rid_seq

    if 'no_rel' in q_json.keys() and q_json['no_rel'].endswith(';'):
        q_json['no_rel'] = q_json['no_rel'][:-1]

    if 'margins' in q_json.keys():
        ml = q_json['margins']
    else:
        ml = list()
    ml.append(1)
    q_json['margins'] = ml
    q_json['beam_wt'] = my_beam_map[top_k_rels[0]]
    return q_json, is_true


def cal_stats(my_args, results, y_true_lengths, op_seq_len, json_obj, qs, split_name):
    op_file = bas_utils.open_file(os.path.join(my_args.job_folder, split_name + '_predictions.txt'))
    all_correct_ct = 0
    cum_op_stats = [0] * (op_seq_len) # cumulative Output Stats
    ind_op_stats = [0] * (op_seq_len) # Individual Output Stats
    fg = [True] * 4
    for i in range(len(results)):
        qid = qs[i]
        next_res = results[i]
        op_string, is_all_correct = '', True
        print_details(next_res, cum_op_stats, ind_op_stats, op_string, fg, False)
        for j in range(len(next_res)):
            ind_op_stats[j] += next_res[j]
            is_one = True
            for k in range(0, (j+1), 1):
                is_one = is_one and next_res[k]
            cum_op_stats[j] += is_one
            op_string += str(next_res[j]) + ','
        for j in range(len(json_obj[qid]['rid_seq'])):
            if not next_res[j]:
                is_all_correct = False
        if is_all_correct:
            all_correct_ct += 1
            json_obj[qid]['predicted_all'] = 1
        op_file.write(op_string[:-1] + '\n')
        json_obj[qid]['pred'] = op_string[:-1]
        fg = print_details(next_res, cum_op_stats, ind_op_stats, op_string, fg, True)
    op_file.close()
    print 'all_correct_ct=' + str(all_correct_ct)
    return cum_op_stats, ind_op_stats, all_correct_ct, json_obj


def print_details(next_res, op_stats, ind_op_stats, op_string, flag, to_mutate):
    return True
    to_print = False
    #print 'All Log - next_res = ' + str(next_res[0]) + ', ' + str(next_res[1]) + ', to_mutate=' + str(to_mutate)
    if (flag[0] and next_res[0] and next_res[1] ) or (flag[1] and next_res[0] and not next_res[1]) or \
            (flag[2] and not next_res[0] and next_res[1]) or (flag[3] and not next_res[0] and not next_res[1]):
        if not to_mutate:
            print '============================================================================='
        print 'next_res = ' + str(next_res[0]) + ', ' + str(next_res[1])
        print 'op_stats[0] = ' + str(op_stats[0]) + ', op_stats[1] = ' + str(op_stats[1])
        print 'ind_op_stats[0] = ' + str(ind_op_stats[0]) + ', ind_op_stats[1] = ' + str(ind_op_stats[1])
        print 'op_string = ' + op_string
        to_print = True
    my_str = ''
    for ops in op_stats:
        my_str += str(ops) + ', '

    if flag[0] and to_mutate and next_res[0] and next_res[1]:   #TT
        print 'TT '
        flag[0] = False
    if flag[1] and to_mutate and next_res[0] and not next_res[1]:   #TF
        flag[1] = False
        print 'TF '
    if flag[2] and to_mutate and not next_res[0] and next_res[1]:   #FT
        flag[2] = False
        print 'FT '
    if flag[3] and to_mutate and not next_res[0] and not next_res[1]:   #FF
        flag[3] = False
        print 'FF '

    if to_print and to_mutate:
        print '-------------------------------------------------------------------------------'
    return flag


def get_distance_margin(mydict):
    ct, cs, d1, d2 = 0, 0.0, 0.0, 0.0
    for key, value in sorted(mydict.iteritems(), key=lambda (k, v): (v, k)):
        ct += 1
        if ct == 1:
            d1 = value
        if ct == 2:
            d2 = value
        if ct > 2:
            break
    margin = d2 - d1
    return margin


def print_results(my_args, cum_op_stats, ind_op_stats, all_correct_ct, results, split_name):
    total_ct = len(results)
    op_file = bas_utils.open_file(os.path.join(my_args.job_folder, split_name + '_results.txt'))
    final_op_string = ''
    for i in range(len(cum_op_stats)):
        final_op_string += str(cum_op_stats[i]) + ','
    for i in range(len(ind_op_stats)):
        final_op_string += str(ind_op_stats[i]) + ','
    final_op_string += str(all_correct_ct) + ','
    percent_right = round(float((float(all_correct_ct) / float(total_ct))*100), 4)
    final_op_string += str(percent_right) + ','
    final_op_string += str(total_ct)
    op_file.write(final_op_string + '\n')
    op_file.close()
    print 'log_folder=' + my_args.job_folder
    print final_op_string


def get_neigbourgood_ents(my_args, g, ent, top_k_rels, all_rel_ids):
    """
    Goal of this function is to find those entities, that are connected to ent, through any of the relations
    present in top_k_rels.
    :param my_args:
    :param g:
    :param ent:
    :param top_k_rels:
    :return: A List of entities for every relation in the top-k relations, as a result it returns list of lists
    """
    ent_list, ct = list(), 0
    for nxt_rel in top_k_rels:
        rel = nxt_rel.split(',')[-1:][0]
        ct += 1
        if ct > my_args.p['beam_size']:
            break
        sd_folder = os.path.abspath(os.path.join(my_args.job_folder, os.pardir, 'saved_data'))
        key = ent + ';' + rel
        global nbr_ent_cache
        if nbr_ent_cache is None and not os.path.isfile(os.path.join(sd_folder, 'nbr_ent_cache.json')):
            nbr_ent_cache = dict()
        elif nbr_ent_cache is None and os.path.isfile(os.path.join(sd_folder, 'nbr_ent_cache.json')):
            nbr_ent_cache = bas_utils.load_json_file(os.path.join(sd_folder, 'nbr_ent_cache.json'))
        if key in nbr_ent_cache.keys():
            ent_list.append(set(nbr_ent_cache[key]))
            continue
        rel_nbr_list = list()
        if ent == '_MYENTMENTION_':
            rel_nbr_list.append('_MYENTMENTION_')
        else:
            for nbr in g.neighbors(ent):
                rels = g[ent][nbr]['relation']
                rel_set = set(rels.split('_'))
                if rel in rel_set:
                    rel_nbr_list.append(nbr)
        nbr_set = list(set(rel_nbr_list))
        nbr_ent_cache[key] = nbr_set
        ent_list.append(nbr_set)
    return ent_list


def get_neigbourgood_rels(my_args, g, ent, my_beam_map, y_pred, y_true, prev_wt, prev_rel, word_index, embed_mats, rmat):
    is_in_kg = False
    for nbr in g.neighbors(ent):
        rels = g[ent][nbr]['relation']
        local_rel_list = rels.split('_')
        for nxt_rel in local_rel_list:
            if nxt_rel in word_index.keys():
                e_nxt_rel = rmat[nxt_rel]
            else:
                print '................. 0 rel......... ATTENTION ...!!! ' + nxt_rel
                continue
            new_rel = prev_rel + ',' + nxt_rel
            if str(new_rel).startswith(','):
                new_rel = new_rel[1:]
            if new_rel in my_beam_map.keys():
                continue
            new_wt = prev_wt * abs(float(get_cosine_similarity(my_args, e_nxt_rel, y_pred)))
            my_beam_map[new_rel] = new_wt
        if y_true in local_rel_list:
            is_in_kg = True
    if y_true is None or y_true == 'None':
        new_rel = prev_rel + ',None'
        my_beam_map[new_rel] = prev_wt
    bm = bas_utils.filter_map(my_map=my_beam_map, isDescending=True, top_k=100)
    return bm, is_in_kg


def add_all_to_beam_map (my_args, all_rel, word_index, embed_mats, rmat, y_pred, y_true, prev_wt, prev_rel, my_beam_map):
    for next_rel in all_rel:
        if next_rel not in word_index.keys():
            print '................. 0 rel......... ATTENTION ...!!! ' + next_rel
            continue
        new_rel = prev_rel + ',' + next_rel
        if new_rel in my_beam_map.keys():
            continue
        e_nxt_rel = rmat[next_rel]
        cos_sim = abs(float(get_cosine_similarity(my_args, e_nxt_rel, y_pred)))
        new_rel = prev_rel + ',' + next_rel
        new_wt = prev_wt * cos_sim
        if str(new_rel).startswith(','):
            new_rel = new_rel[1:]
        my_beam_map[new_rel] = new_wt
    if y_true is None or y_true == 'None':
        new_rel = prev_rel + ',None'
        my_beam_map[new_rel] = prev_wt
    bm = bas_utils.filter_map(my_map=my_beam_map, isDescending=True, top_k=100)
    return bm, True


def get_all_relids(wi):
    sint = bas_utils.ignore_exception(ValueError)(int)
    relid_set = set()
    for w in wi.keys():
        if not str(w).startswith('r'):
            continue
        id = w[1:]
        num = sint(id)
        if num is None:
            continue
        relid_set.add(w)
    return relid_set


def get_cosine_similarity(my_args, x, y):
    return cos_sim_tensorflow(x, y)


def cos_sim_tensorflow(x, y):
    global cos_sim, tf_sess, a, b
    if cos_sim is None:
        a = tf.placeholder(tf.float32, shape=[None], name="input_placeholder_a")
        b = tf.placeholder(tf.float32, shape=[None], name="input_placeholder_b")
        normalize_a = tf.nn.l2_normalize(a, 0)
        normalize_b = tf.nn.l2_normalize(b, 0)
        cos_sim = tf.reduce_sum(tf.multiply(normalize_a, normalize_b))
        tf_sess = tf.Session()
    return tf_sess.run(cos_sim, {a:x, b:y})


if __name__ == '__main__':
    kgrep.test.test_model_eval.main()
    #my_arg_list = bas_utils.pick_arguments('/data/Work-Homes/LOD_HOME/subgraph_webq/temp/')
    #for var in my_arg_list:
    #    print var
