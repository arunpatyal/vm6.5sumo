#!/bin/bash
SCRIPT_PATH=/var/log/vmware

python $SCRIPT_PATH/esx_perf_metrics_6_5.py --server <vcenter server> --target <suko streaming metrics host> --targetPort <target port> --user <username> --password <password> --config_file $SCRIPT_PATH/sumo.json

# Example 1: Using metrics streaming soure and specific log directory with a specific log file prefix.
# python3 $SCRIPT_PATH/esx_perf_metrics_6_5.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --config_file $SCRIPT_PATH/sumo.json --log_file_prefix /var/log/vmware/log/metrics


# Example 2: Using specific log directory with a specific log file prefix and encrypted Password.
# python3 $SCRIPT_PATH/esx_perf_metrics_6_5.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --config_file $SCRIPT_PATH/sumo.json --log_file_prefix /var/log/vmware/log/vsphere_metrics --key 'xgb8NJ3ZYPJbzX6vWHySZbLd73bKWPsGMKoSnry7hL4=' --password 'gAAAAABb6asvlRfxEj_ZQTKOyrqnGNMbfo_kpxrqv4DCO6TorS4FmKFzrepe0_xtiMT67ZT6OOf5bfrVZXNnUDFNlwPWrpFSfg==' --pass_encrypted True

# Example 3: In a case where the cron script run is taking too long because of large infrastructure, following code can be used to continuosly run the script and stream metrics.
# MAKE SURE THAT PIDFILE VARIABLE IN BELOW SCRIPT IS DIFFERENT FOR EACH VCENTER AND DIFFERENT FOR EVENTS AND METRICS.
# Set the CRON expression as * * * * * and use below script.
# SCRIPT_PATH=/var/log/vmware
# PIDFILE=$SCRIPT_PATH/vcenter_server1_metrics.pid
# if [ -f $PIDFILE ]
# then
#   PID=$(cat $PIDFILE)
#   ps -p $PID > /dev/null 2>&1
#   if [ $? -eq 0 ]
#   then
#     echo "Process already running"
#     exit 1
#   else
#     ## Process not found assume not running
#     echo $$ > $PIDFILE
#       python3 $SCRIPT_PATH/esx_perf_metrics_6_5.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --config_file $SCRIPT_PATH/sumo.json --log_file_prefix /var/log/vmware/log/metrics
#   if [ $? -ne 0 ]
#     then
#       echo "Could not create PID file"
#       exit 1
#     fi
#   fi
# else
#   echo $$ > $PIDFILE
#     python3 $SCRIPT_PATH/esx_perf_metrics_6_5.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --config_file $SCRIPT_PATH/sumo.json --log_file_prefix /var/log/vmware/log/metrics
#   if [ $? -ne 0 ]
#   then
#     echo "Could not create PID file"
#     exit 1
#   fi
# fi
#
# rm $PIDFILE
