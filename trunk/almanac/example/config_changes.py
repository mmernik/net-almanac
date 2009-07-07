#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from collections import defaultdict
import pprint
import simplejson


ROUTERDB = "routerdb"
LOGPATH = "logs"

class ConfigEvent(object):
    max_delta_t = timedelta(0,30*60) # 30 minutes
    def __init__(self, timestamp, msg, who, device):
        self.timestamp = timestamp
        self.msg = msg
        self.who = who
        self.devices = [device]
    
    def merge(self, other):
        self.devices.extend(other.devices)
    
    def __eq__(self, other):
        if self.timestamp > other.timestamp:
            delta_t = self.timestamp - other.timestamp
        else:
            delta_t = other.timestamp - self.timestamp
    
        return delta_t <= self.max_delta_t  \
                and self.who == other.who \
                and self.msg == other.msg

class EventTable(object):
    def __init__(self):
        self.events = defaultdict(list)
    
    def add_event(self, event):
        for event0 in self.events[event.msg]:
            if event0 == event:
                event0.merge(event)
                return
    
        self.events[event.msg].append(event)

event_tab = EventTable()

def scan_log(device, logfile, last_time=None):
    """Parse get-config log lines.
    Lines are of the form:
    ' 2008-04-15 16:39: New MIT peering at AofA      Saved by oberman'
    """
    
    lastline = None
    for line in logfile:
        line = line.strip()
    
        # work around cruft in files:
        if line.startswith("< ") or line.startswith("> ") or line.startswith("---"):
            continue
    
        # fix split lines
        if line.startswith("2004-04") and line.find(': ') == -1:
            lastline = line
            continue
    
        if lastline is not None:
            line = "%s: %s" % (lastline, line)
            lastline = None
    
        try:
            (datetime_str, rest) = line.split(": ",1)
        except ValueError:
            #print "A %s skipping: %s" % (device, line)
            continue
    
        try:
            (msg,who) = rest.split("Saved by ", 1)
        except:
            msg = rest
            who = None
    
        msg = msg.strip()
    
        timestamp = None
        for date_fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                timestamp = datetime.strptime(datetime_str, date_fmt)
                break
            except ValueError:
                pass
    
        if timestamp is None:
            #print "B %s skipping: %s" % (device, line)
            continue
    
        event_tab.add_event(ConfigEvent(timestamp, msg, who, device))
    
def get_active_devices():
    devices = []
    for line in open(ROUTERDB):
        line = line.strip()
        (device,type,state) = line.split(":")
        if state == 'up':
            devices.append(device)

    #print devices
    return devices
    
since = datetime(2008, 07, 01)
#print "<!--"
for device in get_active_devices():
#    print device
    logfile = open("%s/%s.log" % (LOGPATH, device))
    scan_log(device, logfile)
#print "-->"

#print "<data>"


#Begin API code here.
#Note: add the file almanac_api.py to the pythonpath first.
import almanac_api
netalmanac = almanac_api.NetAlmanac('http://localhost:8000/net_almanac/event/')

#delete previously created events with the example
events = netalmanac.get_filtered_events(tags=['example'])
for e in events:
    netalmanac.delete_event(e)
    

events = []

for k,v in event_tab.events.iteritems():
    for val in v:
        if val.timestamp < since:
            continue
        
        tag_string = [val.who,'example']
        for dev in val.devices:
            tag_string.append('rtr=' + dev)
        
        e = almanac_api.Event(None,
                              val.msg,
                              'device: ' + ','.join(val.devices) + '; user: ' + val.who,
                              val.timestamp,
                              val.timestamp,
                              '',
                              '',
                              '',
                              tag_string)
        
        events.append(e)
        
for e in events:
    netalmanac.create_event(e)

