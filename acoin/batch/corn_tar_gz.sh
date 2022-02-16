#!/bin/bash
cd /home/firenium/firenium.com/public_html/data/datavault/acoin/batch/log
tar cvfz amazon_coin_scraping_cron_`date "+%Y%m%d"`.tar.gz /home/firenium/firenium.com/public_html/data/datavault/acoin/batch/log/amazon_coin_scraping_cron.log
rm -fr /home/firenium/firenium.com/public_html/data/datavault/acoin/batch/log/amazon_coin_scraping_cron.log
touch /home/firenium/firenium.com/public_html/data/datavault/acoin/batch/log/amazon_coin_scraping_cron.log