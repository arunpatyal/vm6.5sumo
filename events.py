#!/usr/bin/env python
"""
Sumo Logic Script for extracting events from VCenter/ESXI Server
"""
import re
import sys
import datetime
import socket
import argparse
import atexit
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnectNoSSL,Disconnect
import json
import simplejson


def prepareQueryTimeRange(tsFileName,optBeginTime,optEndTime):

    endTime = datetime.datetime.now()
    beginTime = endTime - datetime.timedelta(days=1)
    if optEndTime is not None:
        endTime =  datetime.datetime.strptime(optEndTime, '%Y-%m-%d %H:%M:%S.%f%z')

    if optBeginTime is not None:
        beginTime = datetime.datetime.strptime(optBeginTime, '%Y-%m-%d %H:%M:%S.%f%z')
        # beginTime = int(one_day_ago.timestamp() * 1000)
    else:
        try:
            with open(tsFileName, 'r') as timestampFile:
                for line in timestampFile:
                    print("aaa %s"%line)
                    beginTime = datetime.datetime.strptime(line, '%Y-%m-%d %H:%M:%S.%f%z')
                    print("bbbb %s"%beginTime)
                    #if re.match(r'^#', line) is not None:
                    #    beginTime = re.sub(r'[\n]+', r'', line)
                    #    print("Inside if %s" %begintime)
                    break
            # timestampFile.close()
        except:
            print('Time log not found, will get events 1 day back.')

    return beginTime, endTime


def updateLastReadTime(lastReadTime, tsFileName):
        timestampFile = open(tsFileName, 'w+')
        timestampFile.write(str(lastReadTime))
        timestampFile.close()


def setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server',
                        required=True,
                        action='store',
                        help='Remote ESXi|vCenter Server to connect to')

    parser.add_argument('-o', '--port',
                        required=False,
                        action='store',
                        help="Remote ESXi|vCenter Server port to use, default 443", default=443)

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to server')

    parser.add_argument('-p', '--password',
                        required=True,
                        action='store',
                        help='Password to use when connecting to server')

    parser.add_argument('-f', '--file',
                        required=False,
                        action='store',
                        help='Output Log File.')

    parser.add_argument('-ts', '--timestampFile',
                        required=False,
                        action='store',
                        help='Timestamp File.')

    parser.add_argument('-t', '--target',
                        required=False,
                        action='store',
                        help='Target syslog server.')

    parser.add_argument('-to', '--targetPort',
                        required=False,
                        action='store',
                        help="Target port to use, default 514", default=514)

    parser.add_argument('-bT', '--optBeginTime',
                        required=False,
                        action='store',
                        help='Begin Time to query for the events.')

    parser.add_argument('-eT', '--optEndTime',
                        required=False,
                        action='store',
                        help='End Time to query for the events.')

    args = parser.parse_args()

    if args.target is None and args.file is None:
        sys.exit("Target syslog server or file is required.")

    args = parser.parse_args()

    return args


def convertToDict(obj, oF):

    data = {}
    if not obj:
        return ""
    if type(obj) in (str, int, float, datetime.datetime, bool):
        return str(obj)
    if obj.__class__.mro()[1].__name__ == "Enum":
        return str(obj)
    for k in dir(obj):

        if k.startswith(("__", "_")):
            continue
        try:
            v = getattr(obj, k)
        except vmodl.fault.ManagedObjectNotFound:
            continue
        #if hasattr(obj, "_moId") and hasattr(v, "_moId") and obj == v:
        #    data[k] = str(v)
        # if str(obj) == str(k) == str(v): fails in green and gray

        if type(v) is type or callable(v):
            continue
        oF.write("Keys is::" + str(k) + "::Values is::" + str(v))
        if type(v) is list:
            all_records = []
            for record in v:
                all_records.append(convertToDict(record,oF))
            data[k] = all_records
        elif type(v) is dict:
            all_records_d = []
            for key, record in v.items():
                # print(convertToDict(record))
                all_records_d.append(convertToDict(record,oF))
            data[k] = all_records_d
        elif type(v) in (str, int, float, datetime.datetime, bool):
            data[k] = str(v)
        else:
            data[str(k)] = convertToDict(v,oF)
    return data



def main():
    args = setup_args()

    if args.timestampFile is not None:
        tsFileName = args.timestampFile
    else:
        tsFileName = "timelog"

    if args.server is not None:
        logPrefix = "server: " + args.server + " >>> "

    if args.file == "-":
        outputFile = sys.stdout
    else:
        try:
            outputFile = open(args.file, 'w+')
        except:
            # print("Unable to open %s" % args.file)
            sys.exit(logPrefix + "Unable to open %s" % (args.file))

    # Prepare socket to send
    targetSocket = None
    if args.target is not None:
        try:
            print(logPrefix + "Attempting to connect to TCP log server")
            targetSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(logPrefix + "Socket successfully created")
        except socket.error as err:
            sys.exit(logPrefix + " Socket creation failed with error %s" % (err))

        try:
            # connecting to the server
            targetSocket.connect((args.target, args.targetPort))
            print(logPrefix + "The socket has successfully connected to server %s " % (args.target))
        except socket.error as err:
            sys.exit(logPrefix + "Target server connection failed with error %s" % (err))

   # Prepare time range for query

    beginTime , endTime = prepareQueryTimeRange(tsFileName,args.optBeginTime,args.optEndTime)

    print("1111%s" %beginTime)
    print("222%s" %endTime)
    serverConn = SmartConnectNoSSL(host=args.server,
                           user=args.user,
                           pwd=args.password,
                           port=args.port)
    # serverConn = SmartConnectNoSSL(host="192.168.20.121", user=r"ESXLAB\student1", pwd="Haduc6")
    atexit.register(Disconnect, serverConn)
    separator = ",,,"
    evtCount = 0
    byTime = vim.event.EventFilterSpec.ByTime(beginTime=beginTime, endTime=endTime)
    # eventTypeIds = [
    #     'VirtualVmxnet2','VirtualVmxnet2Option','VirtualVmxnet3','VirtualVmxnet3Option','VirtualVmxnet3Vrdma','VirtualVmxnet3VrdmaOption','VirtualVmxnetOption','VlanProfile','PermissionAddedEvent','VmAcquiredMksTicketEvent','VmAcquiredTicketEvent','VmAutoRenameEvent','VmBeingClonedEvent','VmBeingClonedNoFolderEvent','VmBeingCreatedEvent','VmBeingDeployedEvent'
    #     ]
    # filterSpec = vim.event.EventFilterSpec(time=byTime, eventTypeId=eventTypeIds)
    filterSpec = vim.event.EventFilterSpec(time=byTime)
    eventManager = serverConn.content.eventManager
    eventCollector = eventManager.CreateCollectorForEvents(filterSpec)
    eventCollector.RewindCollector()
    lastReadTime = None
    import ipdb
    ipdb.set_trace()
    while True:
        packetContent = ""
        eventsArray = eventCollector.ReadNextEvents(maxCount=400)
        if len(eventsArray) == 0:
            break
        for event in eventsArray:

            # print(event)
            # print(json.dumps(convertToDict(event), indent=4))
            # print(simplejson.dumps([e.__dict__ for e in event]))
            # print(event)
            # print(evtCount)
            evtCount += 1
            if hasattr(event,'createdTime') and getattr(event, 'createdTime') is not None:
                if event.createdTime.strftime('%Y-%m-%d %H:%M:%S.%f%z') == beginTime
                    continue;
                packetContent = str(event.createdTime) + " "
                lastReadTime = event.createdTime.strftime('%Y-%m-%d %H:%M:%S.%f%z')
            if hasattr(event,'fullFormattedMessage') and getattr(event, 'fullFormattedMessage') is not None:
                fullMsg = str(getattr(event, 'fullFormattedMessage'))
                fullMsg = re.sub(r'[^[:ascii:]]+', r'', fullMsg)
                fullMsg = re.sub(r'[\n]+', r'', fullMsg)
                # print(lastReadTime)
                packetContent = packetContent + separator + " message=" + fullMsg + separator + "user=" + event.userName
            packetContent = packetContent + separator + "eventType=" + str(type(event))
            if hasattr(event,'vm') and getattr(event, 'vm') is not None:
                packetContent = packetContent + separator + "vm=" + event.vm.name
            if hasattr(event,'host') and getattr(event, 'host') is not None:
                packetContent = packetContent + separator + "host=" + event.host.name
            if hasattr(event,'datacenter') and getattr(event, 'datacenter') is not None:
                packetContent = packetContent + separator + "datacenter=" + event.datacenter.name
            if hasattr(event,'computeResource') and getattr(event, 'computeResource') is not None:
                packetContent = packetContent + separator + "computeResource=" + event.computeResource.name
            if hasattr(event,'changeTag') and getattr(event, 'changeTag') is not None:
                packetContent = packetContent + separator + "changeTag=" + event.changeTag.name
            """
            if hasattr(event,'ds) and' getattr(event, 'ds') is not None:
                packetContent = packetContent + separator + "ds=" + event.ds.name
            if hasattr(event,'dvs') and getattr(event, 'dvs') is not None:
                packetContent = packetContent + separator + "dvs=" + event.dvs.name
            if hasattr(event,'net') and getattr(event, 'net') is not None:
                packetContent = packetContent + separator + "net=" + event.net.name
            """
            if hasattr(event,'key') and getattr(event, 'key') is not None:
                packetContent = packetContent + separator + "key=" + str(event.key)
            if hasattr(event,'chainId') and getattr(event, 'chainId') is not None:
                packetContent = packetContent + separator + "chainId=" + str(event.chainId)

            if hasattr(event,'info') and getattr(event, 'info') is not None and getattr(event.info, 'error') is not None:
                packetContent = packetContent + separator + "error=" + str(event.info.error)

            packetContent = packetContent + "\n"

            if outputFile is not None:
                # print(packetContent)
                outputFile.write(packetContent)
                # outputFile.write(str(evtCount))
                #  outputFile.write(str(event))
                # outputFile.write(json.dumps(convertToDict(event, outputFile), indent=4))
                # print(event.__dict__.keys())
                # json.dump(event.__class__.__name__,outputFile
                # obj.__dict__.dump(fullMsg, outputFile)
            if targetSocket is not None:
                targetSocket.send(packetContent)

    print(logPrefix + "%s events collected." % (evtCount))

    if lastReadTime is not None:
        print("%sUpdating timelog with %s ..." % (logPrefix, lastReadTime))
        updateLastReadTime(lastReadTime, tsFileName)
        print(" Done, exiting.")
    elif evtCount != 0:
        print("Error: no last read time")

    if outputFile is not None:
        outputFile.close()

    if targetSocket is not None:
        targetSocket.close()

    # serverConn.disconnect()

if __name__ == '__main__':
    main()
