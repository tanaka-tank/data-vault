#!/bin/bash
cd /home/firenium/firenium.com/public_html/data/datavault/odds_avg/batch/log
tar cvfz boatrace_getodds_script_cron_`date "+%Y%m%d"`.tar.gz /home/firenium/firenium.com/public_html/data/datavault/odds_avg/batch/log/boatrace_getodds_script_cron.log
rm -fr /home/firenium/firenium.com/public_html/data/datavault/odds_avg/batch/log/boatrace_getodds_script_cron.log
touch /home/firenium/firenium.com/public_html/data/datavault/odds_avg/batch/log/boatrace_getodds_script_cron.log