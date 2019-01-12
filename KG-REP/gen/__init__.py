"""
Used for generating questions for KGT (Knowledge Graph Traversal) work

Step-1: First run get_single_path_data.py - this generates single file per path type. See This program for
more documentation.

Step-2: run get_path_pairs.py - this will generate files in folder DP_HOME/wip-data/query_prep/3_path_pair_data
Filename - Film-6-1.csv will indicate that target is Film, and its a combination of the path 1 and path 6
This file will contain - e1, r1, e2, r2, e3

Step-3: Then run the program generate_questions.py to generate questions, this program takes
        templates as input, and also takes files Film-6-1.csv as input to generate these questions

"""