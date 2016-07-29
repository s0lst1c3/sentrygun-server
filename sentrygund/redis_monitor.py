from multiprocessing import Process

def worker(rhost, rport, debug):

    # this is awful but this needs to be ready in three weeks
    import redis 
    import requests

    if debug:
        print '[debug][redis_mon] starting redis monitor'

    r = redis.StrictRedis()
    pubsub = r.pubsub()
    pubsub.psubscribe('*')
    for msg in pubsub.listen():

        if debug:
            print '[debug][redis_mon]', msg

        if 'expired' in msg['channel']:

            msg = msg['data'].split(':')
            alert = [{ 'id' : msg[0], 'location' : msg[1] }]
    
            response = requests.post('http://%s:%d/alert/dismiss' % (rhost, rport), json=alert)

            if debug:
                print '[debug][redis_mon] sent to self:', response

class RedisMon(object):

    def __init__(self, lhost=None, lport=None, debug=False):

        self.lhost = lhost
        self.lport = lport
        self.debug = debug
        self.pid = None

    def start(self):

        args = (self.lhost, self.lport, self.debug,)
        self.pid = Process(target=worker, args=args)

        self.pid.daemon = True
        self.pid.start()

    def stop(self):

        self.terminate()
