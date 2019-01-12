import sys
import json


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


def merge_data(training_data, test_data):
    all_data = list()
    ct = 0
    for next_q in training_data:
        next_q['id'] = 'WebQTrn-' + str(ct)
        next_q['s1'] = 'WebQTrn-' + str(ct)
        all_data.append(next_q)
        ct += 1
    ct = 0
    for next_q in test_data:
        next_q['id'] = 'WebQTest-' + str(ct)
        all_data.append(next_q)
        ct += 1
    print training_data[100]['utterance'] + '----' + training_data[100]['id']
    return all_data


if __name__ == "__main__":
    check_input_arguments()
    training_data = read_data('/data/Work-Homes/LOD_HOME/web-questions/data/webquestions.examples.train.json')
    test_data = read_data('/data/Work-Homes/LOD_HOME/web-questions/data/webquestions.examples.train.json')
    all_data = merge_data(training_data, test_data)

