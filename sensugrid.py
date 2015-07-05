from flask import Flask
from flask import render_template
from flask import abort
import requests
import re
import json
import yaml
import os

app = Flask(__name__)

class Config(object):
    DEBUG = False
    TESTING = False

    with open(os.path.dirname(os.path.abspath(__file__)) + '/conf/config.yaml') as f:
        config = yaml.load(f)

    DCS = config['dcs']
    APPCFG = config['app']


app.config.from_object(Config)
dcs = app.config['DCS']
appcfg = app.config['APPCFG']


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
    except:
        return False


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


def check_stash(stashes, hostname, checkname):
    for s in stashes:
        if re.match('^silence/' + hostname + '/' + checkname + '$', s['path']):
            return True
        if re.match('^silence/' + hostname + '$', s['path']):
            return True
    return False


def agg_data(dc, data, stashes):
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

    for i in data:
        if i['check']['status'] == 0 and not i['check']['name'] == "keepalive":
                ok += 1

        if i['check']['status'] == 1 and not i['check']['name'] == "keepalive":
            if not check_stash(stashes, i['client'], i['check']['name']):
                warn += 1
            else:
                ack += 1

        if i['check']['status'] == 2 and not i['check']['name'] == "keepalive":
            if not check_stash(stashes, i['client'], i['check']['name']):
                crit += 1
            else:
                ack += 1

        if i['check']['name'] == "keepalive" and i['check']['status'] == 2:
            if not check_stash(stashes, i['client'], i['check']['name']):
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


@app.route('/', methods=['GET'])
def root():
    aggregated = []
    for dc in dcs:
        if check_connection(dc):
            aggregated.append(agg_data(dc, get_data(dc), get_stashes(dc)))

    return render_template('data.html', data=aggregated, appcfg=appcfg)


@app.route('/<detail>', methods=['GET'])
def detail(detail):
    data_detail = []
    if dcs:
        for dc in dcs:
            if dc['name'] == detail:
                if check_connection(dc):
                    data_detail = agg_host_data(get_data(dc), get_stashes(dc))
            else:
                abort(404)
    else:
        abort(404)
    return render_template('detail.html', dc=dc, data=data_detail, appcfg=appcfg)


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """
    Returns a json formatted message
    """
    ret = []

    for dc in dcs:
        retdata = {}
        retdata[dc['name']] = {}
        retdata[dc['name']]['url'] = dc['url']
        retdata[dc['name']]['port'] = dc['port']
        if 'user' in dc:
            retdata[dc['name']]['user'] = dc['user']
        if 'password' in dc:
            retdata[dc['name']]['password'] = '********'
        if check_connection(dc):
            retdata[dc['name']]['connected'] = 'True'
            retdata[dc['name']]['error'] = 'False'
        if not check_connection(dc):
            retdata[dc['name']]['connected'] = 'False'
            retdata[dc['name']]['error'] = 'True'
        ret.append(retdata)

    return json.dumps(ret)


if __name__ == '__main__':

    app.run(host='0.0.0.0',
            port=5000)
