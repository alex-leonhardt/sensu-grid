from flask import Flask
from flask import render_template
import requests
import re
import json
import yaml
import argparse

app = Flask(__name__)
data = {}


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


@app.route('/', methods=['GET'])
def root():
    aggregated = []
    for dc in dcs:
        if check_connection(dc):
            aggregated.append(agg_data(dc, get_data(dc), get_stashes(dc)))

    return render_template('data.html', data=aggregated, appcfg=appcfg)


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

    parser = argparse.ArgumentParser(description='Sensu-Grid')
    parser.add_argument("-c", "--config",
                        action="store",
                        help="Full path to configuration file",
                        type=str)
    parser.add_argument("-d", "--debug",
                        help="Run local server with debugging enabled",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    if args.debug:
        _debug = True
    else:
        _debug = False

    try:
        with open(args.config) as f:
            config = yaml.load(f)
    except IOError:
        raise Exception("ERROR: Configuration file not found!")

    dcs = config['dcs']
    appcfg = config['app']

    app.run(host='0.0.0.0',
            debug=_debug)
