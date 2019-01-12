from random import randint
import train_valid_split



def main():
    rel_map = train_valid_split.load_rel_map()
    max_num = len(rel_map)
    for i in range(1, 3000, 1):
        next_num = randint(0, max_num)


if __name__ == '__main__':
    main()
