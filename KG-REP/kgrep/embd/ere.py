import os
import argparse
import networkx as nx
import random
import numpy as np
import utils.basics as bas_utils
import utils.my_map as mm


class MyArgs:
    def __init__(self, run_name='try', embed_size=128, walk_length=10, num_walks=10,
                 window_size=10, epoch_count=1, workers=8):
        self.input = '/data/Work-Homes/LOD_HOME/fb15k2/wip-data/converted-rdf-fb15k.txt'
        self.output = '/data/Work-Homes/LOD_HOME/fb15k/ERE/'+run_name+'.embd'
        self.dimensions = embed_size
        self.walk_length = walk_length
        self.num_walks = num_walks
        self.window_size = window_size
        self.iter = epoch_count
        self.workers = workers


def parse_args():
    parser = argparse.ArgumentParser(description="Run ere.")
    parser.add_argument('--input', nargs='?',
                        default='/data/Work-Homes/LOD_HOME/fb15k2/wip-data/converted-rdf-fb15k.txt',
                        help='Input graph path')
    parser.add_argument('--output', nargs='?', default='/data/Work-Homes/LOD_HOME/fb15k2/model/ere/',
                        help='Embeddings path')
    parser.add_argument('--walk-length', type=int, default=20,
                        help='Length of walk per source. Default is 10.')
    parser.add_argument('--num-walks', type=int, default=20,
                        help='Number of walks per source. Default is 10.')
    args = parser.parse_args()
    if args.learn == 1:
        args.output += 'ere' + '-' + str(args.dimensions) + '-' + str(args.walk_length) + '-' + str(args.num_walks) + \
                       '-' + str(args.window_size) + '.emb'
    else:
        args.output += 'ere' + '-' + str(args.dimensions) + '-' + str(args.walk_length) + '-' + str(args.num_walks) + \
                       '-' + str(args.window_size) + '.txt'
    return args


def read_graph(my_args):
    """
    Reads the input network in networkx.
    :param args:
    :return:
    """
    G = nx.read_edgelist(my_args.input, nodetype=str, data=(('relation', str),), create_using=nx.DiGraph())
    return G


def load_node_map(my_args):
    """
    rel_2_obj - Key = relationship / predicate, Value = List of Objects
    :param my_args:
    :return:
    """
    ct = 0
    node_map = mm.my_map(-1)
    print 'load_node_map() - inp file = ' + my_args.input
    with open(my_args.input) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split()
        subj = toks[0]
        obj = toks[1]
        preds = toks[2]
        ct += 1
        for pred in preds.split('_'):
            if node_map.contains_key(subj):
                rel_2_obj = node_map.get(subj)
            else:
                rel_2_obj = dict()
            if pred in rel_2_obj.keys():
                obj_list = rel_2_obj[pred]
            else:
                obj_list = list()
            obj_list.append(obj)
            rel_2_obj[pred] = obj_list
            node_map.set(subj, rel_2_obj)
            bas_utils.print_status('load_node_map()                ', ct, 100)
    return node_map


def simulate_walks(my_args, g, num_walks, walk_length, node_map):
    '''
    Repeatedly simulate random walks from each node, and relation pair
    '''
    walks, all_node_nbrs = [], {}
    nodes = list(g.nodes())
    for walk_iter in range(num_walks):
        print 'args.output=' + my_args.output
        fn = os.path.join(my_args.output, my_args.run_name + '-' + str(walk_iter) + '-' + '.txt')
        print 'output file name = ' + fn
        of = open(fn, 'w')
        print 'walk_iter=' + str(walk_iter)
        random.shuffle(nodes)
        node_ct, node_total = 0, len(nodes)
        for node in nodes:
            node_ct += 1
            walks, next_start_nodes = walk_rels(node_map, node)
            for i in range(0, len(walks)):
                ere_walk(g, all_node_nbrs, walk_length=walk_length, start_node=next_start_nodes[i],
                         walk=walks[i], op_file=of)
            bas_utils.print_status('/ ' + str(node_total) + ' simulate_walks         ', node_ct, 100)
        of.close()
        print 'ere.ere.learn_embeddings() - walks saved to - ' + my_args.output
    return walks


def walk_rels(node_map, start_node):
    """
    rel_2_map - Key = predicate, Value = list of objects
    :param node_map:
    :param start_node:
    :return:
    """
    walks, next_start_nodes = list(), list()
    rel_2_map = node_map.get(start_node)
    if rel_2_map is None or len(rel_2_map) == 0:
        return walks, next_start_nodes
    if rel_2_map is None:
        print start_node
    for next_rel in rel_2_map.keys():
        next_walk = [start_node, next_rel]
        obj_list = rel_2_map[next_rel]
        if len(obj_list) == 1:
            to_traverse = 0
        else:
            to_traverse = np.random.randint(low=0, high=len(obj_list) - 1)
        next_start_nodes.append(obj_list[to_traverse])
        next_walk.append(obj_list[to_traverse])
        walks.append(next_walk)
    return walks, next_start_nodes


def ere_walk(g, all_node_nbrs, walk_length, start_node, walk, op_file):
    '''
    Simulate a random walk starting from start node.
    '''
    while len(walk) < walk_length:
        cur = walk[-1]
        all_node_nbrs, cur_nbrs = get_neighbors(g, all_node_nbrs, cur)
        if len(cur_nbrs) > 0:
            if len(cur_nbrs) == 1:
                to_traverse = 0
            else:
                to_traverse = np.random.randint(low=0, high=len(cur_nbrs)-1)
            next_rel = cur_nbrs[to_traverse][0]
            next_ent = cur_nbrs[to_traverse][1]
            walk.append(next_rel)
            walk.append(next_ent)
        else:
            break
    if op_file is None:
        return walk
    else:
        op_file.write(bas_utils.to_string(walk, ' ') + '\n')
    return walk


def get_neighbors(g, all_node_nbrs, curr_node):
    """
    This function gets all the triples that have curr_node as subject.
    :param g:
    :param all_node_nbrs:
    :param curr_node:
    :return:
    """
    if len(all_node_nbrs) > 0 and curr_node in all_node_nbrs.keys():
        return all_node_nbrs, all_node_nbrs[curr_node]
    nbrs = list()
    unq_nbr_nodes = g.neighbors(curr_node)
    for next_nbr_ent in unq_nbr_nodes:
        next_relation = g[curr_node][next_nbr_ent]['relation']
        next_relation_list = next_relation.split('_')
        for next_rel in next_relation_list:
            rel_obj = list()
            rel_obj.append(next_rel)
            rel_obj.append(next_nbr_ent)
            nbrs.append(rel_obj)
    sorted_nbrs = sorted(nbrs)
    all_node_nbrs[curr_node] = sorted_nbrs
    return all_node_nbrs, sorted_nbrs


def print_params(myArgs):
    print '1. input='+myArgs.input
    print '2. output='+str(myArgs.output)
    print '3. walk_length='+str(myArgs.walk_length)
    print '4. num_walks='+str(myArgs.num_walks)
    print '------------------------------------------------------------------------------'


def main(given_args):
    '''
    This function is used for generating the ERE embeddings.
    '''
    if given_args is not None:
        args = given_args
    else:
        args = parse_args()
    print_params(args)
    print 'ere.ere.main() - Start Reading the Graph...'
    nx_G = read_graph(args)
    print 'ere.ere.main() - Graph has been read ...'
    print 'ere.ere.main() - Loading RDF in NodeMap ...'
    nm = load_node_map(args)
    print 'ere.ere.main() - RDF NodeMap Loaded ...'
    print 'ere.ere.main() - Walking the graph to generate sequence of nodes...'
    simulate_walks(args, nx_G, args.num_walks, args.walk_length, nm)
    print 'ere.ere.main() - Random Walks Generated ...'


if __name__ == '__main__':
    main(None)
