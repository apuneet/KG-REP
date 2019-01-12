import os

input_dir = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/subgraph'
output_dir = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/wip-data/'

my_objs = set()
for next_file in os.listdir(input_dir):
    if not next_file.endswith('.txt'):
        continue
    print 'next_file=' + next_file
    with open(os.path.join(input_dir, next_file)) as f:
        content = f.readlines()
    for next_line in content:
        toks = next_line.split()
        if len(toks) < 3:
            print next_line
            continue
        next_obj = toks[1]
        my_objs.add(next_obj)
output_file_name = os.path.join(output_dir, 'subgraph-rel.txt')
op_file = open(output_file_name, 'w')
for next_obj in my_objs:
    op_file.write(next_obj + '\n')
op_file.close()
