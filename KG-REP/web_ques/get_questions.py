import os
import utils.basics as bas_utils

working_dir = '/data/Work-Homes/LOD_HOME/web-questions/data'

for next_file in os.listdir(working_dir):
    if not next_file.endswith('json'):
        continue
    print 'next_file=' + next_file
    my_subs = set()
    obj1 = bas_utils.load_json_file(os.path.join(working_dir, next_file))
    output_path_file = os.path.join(working_dir, next_file + '.txt')
    op_file = open(output_path_file, 'w')
    for next_sub in obj1:
        op_file.write(next_sub['utterance'] + '\n')
    op_file.close()
