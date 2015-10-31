import requests
import re

def check_connection(dc):
    url = 'http://{0}:{1}/info'.format(dc['url'], dc['port'])
    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']))
        else:
            r = requests.get(url)
        if r:
            return True
        else:
            return False
    except Exception:
        return False


def check_stash(stashes, hostname, checkname):
    for s in stashes:
        if re.match('^silence/' + hostname + '/' + checkname + '$', s['path']):
            return True
        if re.match('^silence/' + hostname + '$', s['path']):
            return True
    return False

