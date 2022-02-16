#!/bin/bash
export LANG=ja_JP.UTF-8
export PYTHONIOENCODING=utf-8
date "+%Y/%m/%d %H:%M:%S"
PYTHONPATH="/home/firenium/.linuxbrew/bin/python3.9:$PYTHONPATH"
PATH=/home/firenium/.linuxbrew/bin/python3.9:/home/firenium/.linuxbrew/bin:/usr/lib/courier-imap/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/firenium/.composer/vendor/bin:/home/firenium/bin
cd /home/firenium/firenium.com/public_html/data/datavault/
#cd /code/datavault/
python3 manage.py amazon_coin_scraping
date "+%Y/%m/%d %H:%M:%S"