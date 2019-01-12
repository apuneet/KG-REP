import sys
import json
from utils import basics as my_utils


def check_input_arguments():
    if len(sys.argv) < 1:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <epocs> \n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' 10\n')
        sys.exit(1)


def read_data(file_name):
    json_string = ''
    with open(file_name) as f:
            content = f.readlines()
    for next_line in content:
            json_string += next_line
    my_data_obj = json.loads(json_string)
    return my_data_obj


def analyze_data_json(my_data_obj):
    row_count = len(my_data_obj)
    keys = set()
    max_utterance_length, max_url_length, max_targetValue_length = 0, 0, 0
    for next_row in my_data_obj:
        next_keys = next_row.keys()
        for nk in next_keys:
            keys.add(nk)
        my_utterance_length = len(next_row['utterance'])
        my_url_length = len(next_row['url'])
        my_targetValue_length = len(next_row['targetValue'])
        max_utterance_length = max(my_utterance_length, max_utterance_length)
        max_url_length = max(my_url_length, max_url_length)
        max_targetValue_length = max(my_targetValue_length, max_targetValue_length)
        if my_utterance_length > 500:
            print next_row['utterance']
        if my_targetValue_length > 200:
            print 'Q: ' + next_row['utterance']
            print 'A: ' + next_row['targetValue']
        if 'type' in next_row['targetValue']:
            print next_row['targetValue']
    str_keys = my_utils.to_string(keys, ', ')
    print 'Row Count = ' + str(row_count)
    print 'Keys = ' + str_keys
    print 'max_utterance_length = ' + str(max_utterance_length)
    print 'max_url_length = ' + str(max_url_length)
    print 'max_targetValue_length = ' + str(max_targetValue_length)


def get_source_nodes(my_data, src_set, to_print=False):
    for next_row in my_data:
        src_set.add(next_row['url'])
    if not to_print:
        return src_set
    op_file = open('/data/Work-Homes/LOD_HOME/web-questions/wip-data/src-nodes.txt', 'w')
    for i in src_set:
        toks = i.split('/')
        last_item_ct = len(toks) - 1
        op_file.write(i + '\tfb:en.' + toks[last_item_ct] + '\n')
    op_file.close()
    return src_set

if __name__ == "__main__":
    check_input_arguments()
    training_data = read_data('/data/Work-Homes/LOD_HOME/web-questions/data/webquestions.examples.train.json')
    test_data = read_data('/data/Work-Homes/LOD_HOME/web-questions/data/webquestions.examples.train.json')
    #analyze_data_json(training_data)
    my_src_set = get_source_nodes(training_data, set())
    get_source_nodes(test_data, my_src_set, True)

