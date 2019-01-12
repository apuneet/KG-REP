import os
import utils.basics as bas_utils


core_rels_file = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/WebQSP-Core-Relations.txt'
rel_map_pf = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/rel-map-subg2.rdf'
output_file_name = '/data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/missing_rels.txt'


def load_core_rels():
    my_rels, ct = set(), 0
    with open(core_rels_file) as f:
        content = f.readlines()
    for next_line in content:
        ct += 1
        my_rels.add(next_line.replace('\n', ''))
        bas_utils.print_status(' load_core_rels()          ', ct, 1)
    print "\nCore Relations Loaded....."
    return my_rels


def load_rel_map():
    rel_map = dict()
    ct = 0
    with open(rel_map_pf) as f:
        content = f.readlines()
    for next_line in content:
        ct += 1
        toks = next_line.split()
        kg_rel_name = toks[0]
        rel_id = toks[1]
        rel_map[kg_rel_name] = rel_id
        bas_utils.print_status(' load_rel_map()          ', ct, 1)
    print "\nGraph Relations Loaded....."
    return rel_map


def get_missing_rels(s1, s2):
    my_set = set()
    for i in s1:
        if i in s2:
            continue
        else:
            my_set.add(i)
    new_rels = bas_utils.to_string(my_set, '\n')
    op_file = open(output_file_name, 'w')
    op_file.write(new_rels)
    op_file.close()
    print 'output written to ' + output_file_name


if __name__ == "__main__":
    core_rels = load_core_rels()
    graph_rels = load_rel_map()
    get_missing_rels(core_rels, graph_rels.keys())

