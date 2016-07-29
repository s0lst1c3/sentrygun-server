#!/usr/bin/env python
'''
File:   run.py
Author: Gabriel Ryan
Email:  gryan@gdssecurity.com
Source: http://github.com/s0lst1c3/sentrygun_server

Description:

    Driver script for sentrygun-server. Performs the following upon execution:

        1. Parses command line argument to set configuration values
        2. Initializes, configures, and starts redis daemon. 
        3. Spawns a subprocess to monitor redis keyspace events
        4. Spawns Flask-SocketIO instance defined in sentrygund module

Usage:

    python run.py <options go here> 

Command line arguments:

    --port   - specifies the port on which sentrygun-server should listen (defaults to 80)

    --host   - specifies the address at which sentrygun-server should listen (defaults to 0.0.0.0)

    --debug  - Run in debug mode (not recommended for production environments)

    --expire - the number of seconds that alerts should remain active before being
               automatically dismissed

'''


import time
import json
import subprocess

from argparse import ArgumentParser
from sentrygund import sentrygund, socketio, RedisMon

def os_system(command):

    command = command.split()
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, err = p.communicate()

def display_banner():

    print '''
                      __                                     
  ______ ____   _____/  |________ ___.__. ____  __ __  ____  
 /  ___// __ \\ /    \\   __\\_  __ <   |  |/ ___\\|  |  \\/    \\ 
 \\___ \\\\  ___/|   |  \  |  |  | \\/\\___  / /_/  >  |  /   |  \\
/____  >\\___  >___|  /__|  |__|   / ____\\___  /|____/|___|  /
     \\/     \\/     \\/             \\/   /_____/            \\/ 


                    version 1.0.0
                    Gabriel Ryan <gryan@gdssecurity.com>
                    Gotham Digital Science
    '''

    print '[*] Starting on %s:%d . . .' % (sentrygund.config.host, sentrygund.config.port)
    print '[*] Debug mode is', 'on' if sentrygund.config.debug else 'off'
    print '[*] Alerts expiring after %d seconds' % sentrygund.config['EXPIRE']

def set_configs():

    parser = ArgumentParser()

    parser.add_argument('--port',
            required=False,
            type=int,
            default=80,
            help='Run server on this port')

    parser.add_argument('--host',
            required=False,
            type=str,
            default='0.0.0.0',
            help='Run server on this address')

    parser.add_argument('--debug',
            action='store_true',
            default=False,
            help='Run in debug mode.')

    parser.add_argument('--expire',
            dest='expire',
            required=False,
            type=int,
            default=0,
            help=''.join(['Sets the number of seconds that alerts ',
                          'should remain active. Alerts never expire',
                          ' when set to 0 (default).']))

    args = parser.parse_args()

    sentrygund.config.port = args.port
    sentrygund.config.host = args.host
    sentrygund.config.debug = args.debug
    sentrygund.config['EXPIRE'] = args.expire
    sentrygund.config['USE_REDIS'] = args.expire > 0

def main():

    set_configs()

    display_banner()

    if sentrygund.config['USE_REDIS']:
        print '[*] Starting redis-server daemon...'
        os_system('redis-server ./redis.conf')

        time.sleep(2)

    print '[*] Starting SentryGun server...'
    
    try:
    
        print '[*] SentryGun server is running ...'

        redis_mon = RedisMon(sentrygund.config.host,
                        sentrygund.config.port,
                        sentrygund.config.debug)

        if sentrygund.config['USE_REDIS']:
            redis_mon.start()
    
        socketio.run(sentrygund,
                    host=sentrygund.config.host,
                    port=sentrygund.config.port,
                    debug=sentrygund.config.debug)

    except KeyboardInterrupt:

        if sentrygund.config['USE_REDIS']:
            redis_mon.stop()

        print '[*] Gracefully shutting down redis-server'

        # yep, "gracefully"
        os_system('for i in `pgrep redis-server`; do kill $i; done')
        os_system('rm -f dump.rdb')

    print '[*] Goodbye!'

if __name__ == '__main__':
    main()
