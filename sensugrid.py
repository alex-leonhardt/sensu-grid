from __future__ import print_function
from __future__ import unicode_literals
from __future__ import nested_scopes
from __future__ import division
from __future__ import generators

from flask import Flask
from flask import render_template
from flask import abort

from reverseproxied import ReverseProxied
from griddata import *
from gridconfig import *

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from threading import Thread

import json
import time

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

myconfig = DevConfig
app.config.from_object(myconfig)
dcs = app.config['DCS']
appcfg = app.config['APPCFG']


def get_agg_data(q, list):
    while True:
        dc = q.get()
        list.append(agg_data(dc, get_data(dc), get_stashes(dc)))
        q.task_done()
    return list


@app.route('/', methods=['GET'])
def root():

    # _now = time.time()
    aggregated = []
    _queue = Queue()

    for x in range(len(dcs)):
        worker = Thread(target=get_agg_data, args=(_queue,aggregated,))
        worker.setDaemon(True)
        worker.start()

    for dc in dcs:
        # print (dc)
        if check_connection(dc):
            _queue.put(dc)

    _queue.join()

    # _finish = time.time()
    # print (_finish - _now)

    aggregated = sorted(aggregated, key=lambda k: k['name'])
    return render_template('data.html', dcs=dcs, data=aggregated, filter_data=get_filter_data(dcs), appcfg=appcfg)


@app.route('/filtered/<string:subscriptions>', methods=['GET'])
def filtered(subscriptions):
    aggregated = []
    for dc in dcs:
        if check_connection(dc):
            aggregated.append(agg_data(dc, get_data(dc), get_stashes(dc), get_clients(dc), subscriptions))

    return render_template('data.html', dcs=dcs, data=aggregated, filter_data=get_filter_data(dcs), appcfg=appcfg)


@app.route('/show/<string:d>', methods=['GET'])
def showgrid(d):
    data_detail = {}
    if dcs:
        for dc in dcs:
            if dc['name'] == d:
                if check_connection(dc):
                    data_detail = agg_host_data(get_data(dc), get_stashes(dc))
                    if data_detail:
                        break
    else:
        abort(404)
    return render_template('detail.html', dc=dc, data=data_detail, filter_data=get_filter_data(dcs), appcfg=appcfg)


@app.route('/show/<string:d>/filtered/<string:subscriptions>', methods=['GET'])
def showgrid_filtered(d, subscriptions):
    aggregated = {}
    if dcs:
        for dc in dcs:
            if dc['name'] == d:
                if check_connection(dc):
                    aggregated = (agg_host_data(get_data(dc), get_stashes(dc), get_clients(dc), subscriptions))
                    if len(aggregated) > 0:
                        break

    return render_template('detail.html', dc=dc, data=aggregated, filter_data=get_filter_data(dcs), appcfg=appcfg)


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
