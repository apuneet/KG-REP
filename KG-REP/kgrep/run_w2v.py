import sys
import os
import gensim
import re
import utils.basics as bas_utils


dp_home = ''
working_dir = ''


def check_input_arguments():
    if len(sys.argv) < 3:
        sys.stderr.write('Error: Not enough arguments, ')
        sys.stderr.write(sys.argv[0]+' <dp_name> <folder containing ere.txt>\n')
        sys.stderr.write('Example:\n')
        sys.stderr.write('python '+sys.argv[0]+' fb15k model/ere/walk\n')
        sys.stderr.write('python ' + sys.argv[0] + ' webqsp model/ere/walk/\n')
        sys.exit(1)
    global dp_home
    global working_dir
    dp_name = sys.argv[1]
    print 'dp_name=', dp_name
    dp_home = os.path.join(os.environ['WORK_DIR'], dp_name)
    print 'dp_home=', dp_home
    working_dir = os.path.join(dp_home, sys.argv[2])
    print 'working_dir=', working_dir


class MySentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        print 'called - ------------------------------'
        sint = bas_utils.ignore_exception(ValueError)(int)
        for fname in os.listdir(self.dirname):
            if not os.path.isfile(os.path.join(self.dirname, fname)):
                continue
            ct = 0
            print ('Working on file - %s now ...' % fname)
            for next_line in open(os.path.join(self.dirname, fname)):
                nl = ''
                for tok in next_line.split():
                    if tok.endswith('\'s'):
                        ntok = tok[:-2] + ' apostrophe '
                    elif 2020 > sint(tok) > 1000:
                        ntok = tok
                    elif fname.startswith('ere'):
                        ntok = re.sub(r'[^\x00-\x7F]+', ' ',
                                      re.sub(r"[!\"#$%&()*+,-./:;<=>?@\[\]'^_`{|}~\\\t\n]", " ", tok.lower()))
                    else:
                        ntok = re.sub(r'[^\x00-\x7F]+', ' ',
                                      re.sub(r"[!\"#$%&()*+,-./:;<=>?@\[\]0-9'^_`{|}~\\\t\n]",
                                             " ", tok.lower()))
                    nl = nl + ntok + ' '
                yield nl.split()


def run():
    ignore_words_with_frequency = 2
    vector_dimensions = 300
    window_len = 5
    iteratons = 100
    skipg = 1
    sentences = MySentences(working_dir)
    model = gensim.models.Word2Vec(sentences, size=vector_dimensions, window=window_len,
                                   min_count=ignore_words_with_frequency, sg=skipg, iter=iteratons)
    file_name = 'w2v-' + str(vector_dimensions) + '-10-' + str(window_len) + '-'
    file_name = file_name + str(skipg) + '-' + str(iteratons) + '.txt'
    output_file_path = os.path.join(working_dir, os.pardir, file_name)
    model.wv.save_word2vec_format(fname=output_file_path, binary=False)
    print 'Output written to file - ' + output_file_path


if __name__ == '__main__':
    check_input_arguments()
    run()
