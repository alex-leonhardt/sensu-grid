import requests
from gridcheck import *

def get_data(dc):
    url = 'http://{0}:{1}/results'.format(dc['url'], dc['port'])

    if 'user' and 'password' in dc:
        r = requests.get(url, auth=(dc['user'], dc['password']))
    else:
        r = requests.get(url)

    data = r.json()
    r.close()
    return data


def get_stashes(dc):
    url = 'http://{0}:{1}/stashes'.format(dc['url'], dc['port'])

    if 'user' and 'password' in dc:
        r = requests.get(url, auth=(dc['user'], dc['password']))
    else:
        r = requests.get(url)

    data = r.json()
    r.close()
    return data


def agg_data(dc, data, stashes, filters=None):
    """
    Aggregates json data and returns count of ok, warn, crit
    :param data: raw json data
    :return: dc_name, l_ok, l_warn, l_crit
    """
    ok = 0
    warn = 0
    crit = 0
    down = 0
    ack = 0

    if filters and len(filters) > 0:
        filters = filters.split(',')

    for i in data:
        if i['check']['status'] == 0 and not i['check']['name'] == "keepalive":
            if filters and len(filters) > 0:
                for f in filters:
                    if f in i['check']['subscribers']:
                        ok += 1
            else:
                ok += 1

        if i['check']['status'] == 1 and not i['check']['name'] == "keepalive":
            if not check_stash(stashes, i['client'], i['check']['name']):
                if filters and len(filters) > 0:
                    for f in filters:
                        if f in i['check']['subscribers']:
                            warn += 1
                else:
                    warn += 1
            else:
                ack += 1

        if i['check']['status'] == 2 and not i['check']['name'] == "keepalive":
            if not check_stash(stashes, i['client'], i['check']['name']):
                if filters and len(filters) > 0:
                    for f in filters:
                        if f in i['check']['subscribers']:
                            crit += 1
                else:
                    crit += 1
            else:
                ack += 1

        if i['check']['name'] == "keepalive" and i['check']['status'] == 2:
            if not check_stash(stashes, i['client'], i['check']['name']):
                # we cannot currently apply filters as keepalive checks do not have subscribers/subscriptions
                down += 1
            else:
                ack += 1

    return {"name": dc['name'], "ok": ok, "warning": warn, "critical": crit, "down": down, "ack": ack}


def agg_host_data(data, stashes):
    """
    returns: a dict of {"hostname": [list,of,alert,statuses], "hostname2": [list,of,alert,statuses]}
    """

    _data = data
    _stashes = stashes

    retdata = {}

    for check in _data:
        _host = check['client']
        retdata[_host] = []

    for check in _data:
        _host = check['client']
        if check['check']['status'] and check['check']['name'] != 'keepalive':
            if not check_stash(_stashes, _host, check['check']['name']):
                retdata[_host].append(check['check']['status'])
        if check['check']['status'] and check['check']['name'] == 'keepalive':
            retdata[_host].append(-1)

    return retdata
