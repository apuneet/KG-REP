"""
Step-0: keep a backup of subg3.rdf as subg3.rdf.orig
        replace " " (space) by "_" (underscore) in the subg3.rdf
        make a folder subgraph_webq/wip-data-3
        copy subg3.rdf here
        make copies of this file as - subg3_node_list.txt and as subg3_rel_list.txt

        in subg3_node_list.txt, remove the "." at the end of every line
        using awk print first term and third term separated by "\n", then run sort -u on this file

        in subg3_rel_list.txt, run awk to get second  term only, and then run sort -u

Step-1: Given an edge list, of a knowledge graph, run the program graph/convert_rdf_2_integer_form.py
        This program takes a bit long to run, it may take more than 30 min.
        For a description of this program see its documentation. (it took 10 min on 24th Sep 2018)

        This program mainly converts the knowledge graph into a form readable by networkx and also creates
        the node-map and relation-map files.

        rename converted-rdf-subg2.rdf to converted-rdf-subgraph_webq.rdf in the folder
        /data/Work-Homes/LOD_HOME/subgraph_webq/wip-data

Step-2: using the script /data/Work-Homes/LOD_HOME/FB_SEMPRE/create-subgraph/scr/check_if_rel_present.sh
        find the relations that are not present in subgraph or in full graph
        make a copy of rel-map-subg<n>.rdf as rel-map-subg<n>-manual.rdf and add the missing relations at the end
        for example see - /data/Work-Homes/LOD_HOME/subgraph_webq/wip-data-3/rel-map-subg3-manual.rdf

Step-3: Run program web_ques.get_qid_sid_mapping.py This will create a file
        /data/Work-Homes/LOD_HOME/subgraph_webq/wip-data/final_qid_sid_mapping.txt
        This file is used by train_valid_split

Step-4: For fb15k2 - To prepare the data, first go to package gen, and follow instructions.
        For WebQSP - run the program web_ques/train_valid_splitv3.py

Step-5: Run progs in kgt/embd/ to obtain the embeddings

Step-6: model_stqa.py: This program internally calls load_prepare_data.py before the deep-learning part,
        and calls run_model_eval.py after that.
        Before calling this main program following things need to be ready.
        1.  ERE + Word Embedding
        2.  Questions and corresponding relation sequences in a specific format
        3.


"""