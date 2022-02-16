#!/bin/bash
export LANG=ja_JP.UTF-8
export PYTHONIOENCODING=utf-8
PYTHONPATH="/home/firenium/.linuxbrew/bin/python3.9:$PYTHONPATH"
PATH=/home/firenium/.linuxbrew/bin/python3.9:/home/firenium/.linuxbrew/bin:/usr/lib/courier-imap/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/firenium/.composer/vendor/bin:/home/firenium/bin
date "+%Y/%m/%d %H:%M:%S"
cd /home/firenium/firenium.com/public_html/data/datavault/
python3 manage.py boatrace_info_batch
date "+%Y/%m/%d %H:%M:%S"