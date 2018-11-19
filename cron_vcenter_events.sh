#!/bin/bash
SCRIPT_PATH=/var/log/vmware

python $SCRIPT_PATH/events.py --server <vcenter server> --target <syslog host> --targetPort <syslog port> --user <username> --password <password> -file <output_filename> 2>&1 | /bin/logger

# Example
# python $SCRIPT_PATH/events.py --server 192.168.124.29 --target vmahost --targetPort 1514 --user sumoadmin --password sumoadmin -file /var/log/vmware/output/vsphere_events 2>&1 | /bin/logger
