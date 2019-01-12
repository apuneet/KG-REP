import os

input_dir = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/'
output_dir = '/data/Work-Homes/LOD_HOME/FB_SEMPRE/subjects/'

for next_file in os.listdir(input_dir):
    if not next_file.startswith('0.ttl'):
        continue
    print 'next_file=' + next_file
    my_subs = set()
    with open(os.path.join(input_dir, next_file)) as f:
        content = f.readlines()
    for next_line in content:
        next_sub = next_line.split()[0]
        my_subs.add(next_sub)
    output_file_name = os.path.join(output_dir, next_file)
    op_file = open(output_file_name, 'w')
    for next_sub in my_subs:
        op_file.write(next_sub + '\n')
    op_file.close()
