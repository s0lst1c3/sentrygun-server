import re
import bleach
import time

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
