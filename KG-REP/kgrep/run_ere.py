import sys
import os
import utils.basics as bas_utils
import kgrep.embd.ere as ere


def check_input_arguments():
    if len(sys.argv) < 2:
        sys.stderr.write('Error: Not enough arguments. \n')
        sys.stderr.write('Help: Set all parameters in ere.conf, and provide its path-name as argument.\n')
        sys.stderr.write(sys.argv[0] + ' run_conf/ere.conf\n')
        sys.exit()
    conf_path_file = sys.argv[1]
    return conf_path_file


def parse_params(conf_pf):
    p = dict()
    sint = bas_utils.ignore_exception(ValueError)(int)
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
        p[toks[0]] = val
    word_dir = os.environ['WORK_DIR']
    p['dp_home'] = os.path.join(word_dir, p['dp_name'])
    args = MyArgs(p)
    print '========================================================='
    return args


class MyArgs:
    def __init__(self, ip):
        self.input = os.path.join(ip['dp_home'], 'kg/converted-rdf-' + ip['dp_name'] + '.rdf')
        self.output = os.path.join(ip['dp_home'], ip['output_folder_suffix'], 'temp')
        self.walk_length = ip['walk_length']
        self.num_walks = ip['num_walks']
        self.run_name = ip['run_name']
        self.p = ip


def strip_walk(ere_folder):
    file_name = os.path.join(ere_folder, os.pardir, 'walk/ere.txt')
    op_file = open(file_name, 'w')
    for next_file in os.listdir(ere_folder):
        if not os.path.isfile(os.path.join(ere_folder, next_file)):
            continue
        with open(os.path.join(ere_folder, next_file)) as f:
            content = f.readlines()
        for next_line in content:
            toks = next_line.split()
            if len(toks) < 2:
                continue
            op_file.write(next_line)
    op_file.close()
    print '\n Final output written to file - ' + file_name


if __name__ == '__main__':
    conf_file = check_input_arguments()
    args = parse_params(conf_file)
    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    final_output_dir = os.path.join(args.output, os.pardir, 'walk')
    if not os.path.isdir(final_output_dir):
        os.mkdir(final_output_dir)
    ere.main(args)
    strip_walk(args.output)
