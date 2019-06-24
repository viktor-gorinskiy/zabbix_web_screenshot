#!/usr/bin/python3.4
import zabbixlib

def off_trigge(eventid,messages):

    params = {
            "eventids": eventid,
            "message": messages,
            "action": "0"
        }

    result = zabbixlib.zabbix(method = 'event.acknowledge', params=params)
    return result

