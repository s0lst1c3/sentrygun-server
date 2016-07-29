#!/usr/bin/env python
'''
Module: sentrygund
Author: Gabriel Ryan
Email:  gryan@gdssecurity.com
Source: http://github.com/s0lst1c3/sentrygun_server

Description:
    
    This module contains the majority of sentrygun-servers MVC code.

'''

import os

from flask import Flask
from flask_socketio import SocketIO

sentrygund = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
#sentrygund.config.from_pyfile('./config.py')
sentrygund.config.from_object('config')

socketio = SocketIO(sentrygund)

from sentrygund import models, views
from redis_monitor import RedisMon
