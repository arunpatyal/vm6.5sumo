#!/bin/bash
SCRIPT_PATH=/var/log/vmware

python $SCRIPT_PATH/esx_perf_metrics_6_5.py --server <vcenter server> --target <connector streaming metrics host> --targetPort <target port> --user <username> --password <password> -config_file <config_filename> 2>&1 | /bin/logger

# Example
# python $SCRIPT_PATH/esx_perf_metrics_6_5.py --server 192.168.124.29 --target vmahost --targetPort 1514 --user sumoadmin --password sumoadmin -config_file sumo.json 2>&1 | /bin/logger
