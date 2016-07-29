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
import sys

from argparse import ArgumentParser
from sentrygund import sentrygund, socketio, RedisMon, utils
from multiprocessing import Process

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
            help='Specifies the port on which sentrygun-server should listen (defaults to 80)')

    parser.add_argument('--host',
            required=False,
            type=str,
            default='0.0.0.0',
            help='Specifies the address at which sentrygun-server should listen (defaults to 0.0.0.0)')

    parser.add_argument('--debug',
            action='store_true',
            default=False,
            help='Run in debug mode (not recommended for production environments)')

    parser.add_argument('--expire',
            dest='expire',
            required=False,
            type=int,
            default=0,
            help=''.join(['Sets the number of seconds that alerts ',
                          'should remain active before they are ',
                          'automatically dismissed. To disable alert ',
                          'expiration, set this to 0 (default).']))

    parser.add_argument('--tunnels',
            dest='tunnels',
            required=False,
            type=str,
            nargs='+',
            metavar='dest',
            help=''.join(['Create an ssh tunnel from localhost:PORT on ',
                        'sentrygun-server to localhost:PORT on a list ',
                        'of of sentrygun clients, where PORT is the port ',
                        'at which sentrygun-server listens on. When this ',
                        'flag is used, sentrygun-server will always listen ',
                        'on localhost regardless of whether the --host is ',
                        'used. Use this option when running sentrygun on a ',
                        'hostile network. Sentrygun clients should be ',
                        'specified with the format user@host:port.']))

    args = parser.parse_args()

    sentrygund.config['TUNNELS'] = args.tunnels
    sentrygund.config.port = args.port
    sentrygund.config.host = '127.0.0.1' if args.tunnels is None else args.host
    sentrygund.config.debug = args.debug
    sentrygund.config['EXPIRE'] = args.expire
    sentrygund.config['USE_REDIS'] = args.expire > 0

def main():

    set_configs()

    if sentrygund.config['TUNNELS'] is not None:
        utils.create_reverse_tunnels()

    display_banner()

    if sentrygund.config['USE_REDIS']:
        print '[*] Starting redis-server daemon...'
        utils.os_system('redis-server ./redis.conf')

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

        if sentrygund.config['TUNNELS'] is not None:
            utils.destroy_reverse_tunnels()

        if sentrygund.config['USE_REDIS']:
            redis_mon.stop()

            print '[*] Gracefully shutting down redis-server'

            # yep, "gracefully"
            utils.os_system('for i in `pgrep redis-server`; do kill $i; done')
            utils.os_system('rm -f dump.rdb')

    print '[*] Goodbye!'

if __name__ == '__main__':
    main()
