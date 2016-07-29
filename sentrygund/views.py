#!/usr/bin/env python
'''
File:   views.py
Module: sentrygund
Author: Gabriel 'solstice' Ryan
Email:  gryan@gdssecurity.com
Source: http://github.com/s0lst1c3/sentrygun-server

Description:
    
    This file is split up into sections:

        EVENTS:
        
            Ajax requests from the web interface or a sentrygun sensor client.
            Events trigger an I/O call or an Action. 

        SOCKETIO EVENTS:

            Similar to EVENTS, but are triggered in response to received over 
            websocket protocol.

        ACTIONS:

            Actions are commands broadcast to socketio clients that cause them
            them to perform some task. Actions are sent to webclients,
            sentrygun sensors, or both.

        VIEWS:
    
            Views render HTML using the Jinja templating engine.
'''

import json
import time

import models
import utils

from flask import render_template, request, Response, session
from flask_socketio import emit, disconnect

from sentrygund import sentrygund, socketio

# this variable exists to make future user management implementations easier
clients = []

socketio_ns = sentrygund.config['SOCKETIO_NS']
listener_ns = sentrygund.config['LISTENER_NS']

# ERROR HANDLERS -------------------------------------------------------------------
@sentrygund.errorhandler(400)
def bad_request(error='Bad request'):

    data = json.dumps({
        'success' : False,
        'status' : 400,
        'details' : error,
    })
    return Response(data, status=400, mimetype='application/json')
    



# AJAX EVENTS ----------------------------------------------------------------------

@sentrygund.route('/alert/add', methods=['POST'])
def on_alert_add():

    if request.headers['Content-Type'] != 'application/json':
        bad_request(error='Content-Type must be application/json')

    alert = request.get_json(force=False)

    try:
        alert = utils.sanitize_alert(alert)
    except AssertionError:
        bad_request()

    add_alert(alert)

    data = {'success' : True, 'status' : 200} 
    return Response(data, status=200, mimetype='application/json')

@sentrygund.route('/alert/dismiss', methods=['POST'])
def on_alert_dismiss():

    if request.headers['Content-Type'] != 'application/json':
        bad_request(error='Content-Type must be application/json')

    alerts = request.get_json(force=False)

    for a in alerts:
        
        if 'id' not in a or not utils.is_int(a['id']):
            bad_request()
            

    if sentrygund.config.debug:
        print '[debug][views] dismissing:', json.dumps(alerts, indent=4)
    dismiss_alerts(alerts)

    data = {'success' : True, 'status' : 200} 
    return Response(data, status=200, mimetype='application/json')

@sentrygund.route('/napalm', methods=['POST'])
def on_napalm():

    if request.headers['Content-Type'] != 'application/json':
        bad_request(error='Content-Type must be application/json')

    targets = request.get_json(force=False)

    if sentrygund.config.debug:
        print '[debug][views] received request for napalm attack'

    for t in targets:

        if 'id' not in t or not utils.is_int(t['id']):
            bad_request()
    
        t = models.retrieve_alert(t)

        if sentrygund.config.debug:
            print '[debug][views] calling launch_napalm() on:',
            print json.dumps(t, sort_keys=True, indent=4)
        launch_napalm(t)

    data = {'success' : True, 'status' : 200}
    return Response(data, status=200, mimetype='application/json')

@sentrygund.route('/deauth', methods=['POST'])
def on_deauth():

    if request.headers['content-type'] != 'application/json':
        bad_request(error='content-type must be application/json')

    targets = request.get_json(force=False)

    if sentrygund.config.debug:
        print '[debug][views] received request for deauth attack'

    for t in targets:
    
        if 'id' not in t or not utils.is_int(t['id']):
            bad_request()
    
        t = models.retrieve_alert(t)

        if sentrygund.config.debug:
            print '[debug][views] calling launch_deauth() on:',
            print json.dumps(t, sort_keys=True, indent=4)
        launch_deauth(t)

    data = {'success' : True, 'status' : 200} 
    return Response(data, status=200, mimetype='application/json')

@sentrygund.route('/webcli/connect', methods=['GET'])
def on_webcli_connect():

    current_alerts = models.retrieve_alerts()

    if sentrygund.config.debug:
        print '[debug][views] retrieving all alerts:',
        print json.dumps(current_alerts, indent=4)

    data = json.dumps(current_alerts)
    response = Response(data, status=200, mimetype='application/json')

    return response

# ACTIONS ---------------------------------------------------------------------

def dismiss_alerts(alerts):
    
    models.remove_alerts(alerts)

    if sentrygund.config.debug:
        print '[debug][views] received dismiss request'
    emit('dismiss alerts', alerts, namespace=socketio_ns, broadcast=True)

    # stop all current attacks
    for a in alerts:

        a['dismiss'] = True
        launch_napalm(a)
        launch_deauth(a)

def add_alert(alert):

    
    alert = models.store_alert(alert)

    if sentrygund.config.debug:
        print '[debug][views] received add request for:',
        print json.dumps(alert, sort_keys=True, indent=4)

    emit('add alert', alert, namespace=socketio_ns, broadcast=True)

def launch_napalm(alerts):

    emit('napalm_target', alerts, namespace=listener_ns, broadcast=True)

def launch_deauth(alerts):
    emit('deauth_target', alerts, namespace=listener_ns, broadcast=True)

# SOCKETIO EVENTS -------------------------------------------------------------

@socketio.on('connected', namespace=socketio_ns)
def watchdog_connect():

    if sentrygund.config.debug:
        print '[debug][views] %s connected' % (request.sid)
    clients.append(request.sid)

@socketio.on('disconnect request', namespace=socketio_ns)
def watchdog_disconnect_request():

    if sentrygund.config.debug:
        print '[debug][views] %s connected' % (request.sid)
    clients.remove(request.sid)
    
    disconnect()

# VIEWS -----------------------------------------------------------------------

@sentrygund.route('/')
def index():

    return render_template('index.html')

@sentrygund.route('/prev')
def prev():

    return render_template('prev.html')

@sentrygund.route('/map')
def area_map():

    return render_template('map.html')

@sentrygund.route('/settings')
def settings():

    return render_template('settings.html')

@sentrygund.route('/logout')
def logout():

    return 'logout page goes here'
