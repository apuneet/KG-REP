
class my_map:
    hp = ''
    my_dict = dict()
    max_ct = 0

    def __init__(self, hash_position):
        self.hp = hash_position

    def contains_key(self, key):
        parti_char = key[self.hp-1:self.hp]
        if parti_char not in self.my_dict.keys():
            return False
        else:
            key_parti = self.my_dict[parti_char]
        if key not in key_parti.keys():
            return False
        else:
            return True

    def set(self, key, val):
        if not self.contains_key(key):
            self.max_ct += 1
        parti_char = key[self.hp-1:self.hp]
        if parti_char not in self.my_dict.keys():
            key_parti = dict()
        else:
            key_parti = self.my_dict[parti_char]
        key_parti[key] = val
        self.my_dict[parti_char] = key_parti
        return val

    def get(self, key):
        val = None
        parti_char = key[self.hp-1:self.hp]
        if parti_char not in self.my_dict.keys():
            key_parti = dict()
        else:
            key_parti = self.my_dict[parti_char]
        if key in key_parti.keys():
            val = key_parti[key]
        key_parti[key] = val
        return val

    def size(self):
        return self.max_ct

    def calculate_size(self):
        ct = 0
        for next_parti_char in self.my_dict.keys():
            for next_key in self.my_dict[next_parti_char].keys():
                ct +=1
        return ct

    def print_to_file(self, path_file, key_val_sep):
        op_file = open(path_file, 'w')
        for next_parti_char in self.my_dict.keys():
            for next_key in self.my_dict[next_parti_char].keys():
                op_file.write(str(next_key) + key_val_sep + str(self.my_dict[next_parti_char][next_key]) + '\n')
        op_file.close()


if __name__ == '__main__':
    mm = my_map(-1)
    print mm.contains_key('abcd')
    mm.set('abcd', 10)
    print mm.contains_key('abcd')
    print mm.get('abcd')
    print mm.size()
