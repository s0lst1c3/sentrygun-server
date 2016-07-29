import re
import bleach
import time
import subprocess
from sentrygund import sentrygund

def os_system(command):

    command = command.split()
    print command
    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, err = p.communicate()

def is_int(n):

    try:
        its_an_int = int(n) == float(n)
    except ValueError:
        its_an_int =  False
    return its_an_int

def is_float(n):

    try:
        float(n)
        return True
    except ValueError:
        return False

def is_mac_addr(n):

    return re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", n.lower())

def sanitize_alert(alert):

    assert alert.keys() == ['bssid', 'tx', 'timestamp', 'intent', 'location', 'id', 'channel', 'essid']

    assert is_int(alert['id'])

    alert['location'] = bleach.clean(alert['location'])

    assert is_mac_addr(alert['bssid'])

    assert type(alert['channel']) == int
    assert alert['channel'] > 0 and alert['channel'] < 14

    assert is_int(alert['tx'])

    alert['essid'] = bleach.clean(alert['essid'])

    alert['intent'] = bleach.clean(alert['intent'])

    assert is_float(alert['timestamp'])

    return alert

def create_reverse_tunnels():

    identity_file = sentrygund.config['IDENTITY_FILE']
    for index, sensor in enumerate(sentrygund.config['TUNNELS']):
        sensor = sensor.split(':')
        if len(sensor) > 1:
            ssh_port = int(sensor[1])
        else:
            ssh_port = 22
        rhost = sensor[0]
        lport = sentrygund.config.port
        autossh_out = index+10035
        
        os_system('./scripts/open_botnet.sh %s %d %s %d %d' %\
            (identity_file, ssh_port, rhost, lport, autossh_out))

def destroy_reverse_tunnels():

    os_system('./scripts/kill_autossh.sh')

    print "[*] Cleaning up remaining connections on remote sensors..."
    for index, sensor in enumerate(sentrygund.config['TUNNELS']):
        sensor = sensor.split(':')
        if len(sensor) > 1:
            ssh_port = int(sensor[1])
        else:
            ssh_port = 22
        rhost = sensor[0]
    
        os_system('./scripts/close_botnet.sh %s %d' % (rhost, ssh_port))
