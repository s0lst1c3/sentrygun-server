#!/usr/bin/env python
'''
File:   models.py
Module: sentrygund
Author: Gabriel Ryan
Email:  gryan@gdssecurity.com
Source: http://github.com/s0lst1c3/sentrygun-server

Description:
    
    This file represents the model in sentrygun-server's MVC architecture. All
    calls to databases and storage happen here.

'''

import json
import redis

from sentrygund import sentrygund

current_alerts = {}

def store_alert(alert):
    
    global current_alerts

    if sentrygund.config['USE_REDIS']:

        r = redis.Redis()
        r.set('%s:%s' % (alert['id'], alert['location']), alert['location'])
        r.expire('%s:%s' % (alert['id'], alert['location']), sentrygund.config['EXPIRE'])

    _id = alert['id']

    if _id in current_alerts:

        current_alerts[_id]['timestamp'] = alert['timestamp']
        current_alerts[_id]['locations'][alert['location']] = alert['tx']

    else:

        current_alerts[_id] = alert
        current_alerts[_id]['locations'] = { alert['location'] : alert['tx'] }

    return current_alerts[_id]

def retrieve_alerts():

    all_alerts = []
   
    return current_alerts.values()

def retrieve_alert(a):

    if sentrygund.config['DEBUG']:

        print '[debug] models.py - current_alerts is:',
        print json.dumps(current_alerts, indent=4, sort_keys=True)

    return current_alerts[a['id']]

def remove_alerts(alerts):
    
    global current_alerts

    for a in alerts:

        if a['id'] in current_alerts:
            
            if sentrygund.config['DEBUG']:
                print '[debug] models.py - removing from', json.dumps(current_alerts, indent=4, sort_keys=True)

            del current_alerts[a['id']]
