#!/bin/bash

export WORK_DIR=/data/DATA_HOME/
cd ../
echo "python kgt1/model_stqa.py run_conf/webqsp.conf"
python kgrep/model_stqa.py run_conf/webqsp.conf
echo "=========================================================================="
echo ".... Finished Running Model"
