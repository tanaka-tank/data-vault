#!/bin/bash
export LANG=ja_JP.UTF-8
export PYTHONIOENCODING=utf-8
date "+%Y/%m/%d %H:%M:%S"
#cd /home/firenium/firenium.com/public_html/data/datavault/
cd /code/datavault/
python3 manage.py boatrace_info_batch
date "+%Y/%m/%d %H:%M:%S"