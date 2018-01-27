import requests
import re


def check_connection(dc):
    url = 'http://{0}:{1}/info'.format(dc['url'], dc['port'])
    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']), timeout=30)
        else:
            r = requests.get(url, timeout=30)
        if r:
            return True
        else:
            return False
    except Exception:
        return False


def check_stash(stashes, hostname, checkname):
    for s in stashes:
        if re.match('^client:' + hostname + ':' + checkname + '$', s['id']):
            return True
        if re.match('^client:' + hostname + ':\*', s['id']):
            return True
    return False
