import sys
import os

output_folder = '/data/Work-Homes/LOD_HOME/web-questions/wip-data'


def get_linked_entities(file_name, my_entities):
    my_folder = '/data/Work-Homes/LOD_HOME/web-questions/S-Mart-Entity-Linking/STAGG-master'
    with open(os.path.join(my_folder, file_name)) as f:
            content = f.readlines()
    for next_line in content:
        next_ent = next_line.split('\t')[4]
        my_entities.add(next_ent)
    return my_entities


def check_input_arguments():
    if len(sys.argv) < 1:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <epocs> \n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' 10\n')
        sys.exit(1)


if __name__ == "__main__":
    check_input_arguments()
    my_entities = set()
    my_ent_set = get_linked_entities('webquestions.examples.train.e2e.top10.filter.sid.tsv', my_entities)
    my_ent_set = get_linked_entities('webquestions.examples.test.e2e.top10.filter.sid.tsv', my_ent_set)
    op_file = open(os.path.join(output_folder, 'linked-entities.txt'), 'w')
    for next_ent in my_ent_set:
        op_file.write(next_ent + '\n')
    op_file.close()
    print len(my_ent_set)

