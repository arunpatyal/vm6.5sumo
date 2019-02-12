#!/bin/bash
SCRIPT_PATH=/var/log/vmware

python $SCRIPT_PATH/events.py --server <vcenter server> --target <syslog host> --targetPort <syslog port> --user <username> --password <password> -file <output_filename_path_and_prefix>

# Example 1: Using a file output, use a local or remote file source in this case.
# python $SCRIPT_PATH/events.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --file /var/log/vmware/output/vsphere_events


# Example 2: Using syslog and specific log directory with a specific log file prefix. Use a syslog source to ingest the logs.
# python $SCRIPT_PATH/events.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --log_file_prefix /var/log/vmware/log/vsphere_events

# Example 3: Using syslog and specific log directory with a specific log file prefix and encrypted Password. Use a syslog source to ingest the logs.
# python $SCRIPT_PATH/events.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --key 'xgb8NJ3ZYPJbzX6vWHySZbLd73bKWPsGMKoSnry7hL4=' --password 'gAAAAABb6asvlRfxEj_ZQTKOyrqnGNMbfo_kpxrqv4DCO6TorS4FmKFzrepe0_xtiMT67ZT6OOf5bfrVZXNnUDFNlwPWrpFSfg==' --pass_encrypted True --log_file_prefix /var/log/vmware/log/vsphere_events

# Example 4: In a case where the cron script run is taking too long because of large infrastructure, following code can be used to continuosly run the script and retrieve events.
# MAKE SURE THAT PIDFILE VARIABLE IN BELOW SCRIPT IS DIFFERENT FOR EACH VCENTER AND DIFFERENT FOR EVENTS AND METRICS.
# Set the CRON expression as * * * * * and use below script.
# SCRIPT_PATH=/var/log/vmware
# PIDFILE=$SCRIPT_PATH/vcenter_server1_events.pid
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
#     python3 $SCRIPT_PATH/events.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --file /var/log/vmware/output/vsphere_events
#     if [ $? -ne 0 ]
#     then
#       echo "Could not create PID file"
#       exit 1
#     fi
#   fi
# else
#   echo $$ > $PIDFILE
#     python3 $SCRIPT_PATH/events.py --server 192.168.124.29 --target sumologic_host --targetPort sumologic_host_port --user sumoadmin --password sumoadmin --file /var/log/vmware/output/vsphere_events
#   if [ $? -ne 0 ]
#   then
#     echo "Could not create PID file"
#     exit 1
#   fi
# fi
#
# rm $PIDFILE
