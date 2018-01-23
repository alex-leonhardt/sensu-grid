from __future__ import print_function
from __future__ import unicode_literals
from __future__ import nested_scopes
from __future__ import division
from __future__ import generators

from flask import Flask
from flask import render_template
from flask import abort

from reverseproxied import ReverseProxied
from gridcheck import check_connection
from griddata import (
    agg_data,
    get_data,
    agg_host_data,
    get_stashes,
    get_filter_data,
    get_clients,
    get_events
)
from gridconfig import DevConfig

from multiprocessing.dummy import Pool as ThreadPool
# https://stackoverflow.com/questions/2846653/how-to-use-threading-in-python

import json
import logging
import logging.config


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

myconfig = DevConfig
app.config.from_object(myconfig)
dcs = app.config['DCS']
appcfg = app.config['APPCFG']
timeout = appcfg.get('requests_timeout', 10)
log_level = appcfg.get('logging_level', 'INFO').upper()
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "requests": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False
        },
        "sensugrid": {
            "level": log_level,
            "handlers": ["console"],
            "propagate": False
        },
        "gridcheck": {
            "level": log_level,
            "handlers": ["console"],
            "propagate": False
        },
        "gridconfig": {
            "level": log_level,
            "handlers": ["console"],
            "propagate": False
        },
        "griddata": {
            "level": log_level,
            "handlers": ["console"],
            "propagate": False
        },
    },
    "": {
        "level": log_level,
        "handlers": ["console"]
    }
})
LOGGER = logging.getLogger(__name__)


# Python3 doesn't have cmp
def _cmp(x, y):
    return (x > y) - (x < y)


def get_agg_data(dc):
    r = agg_data(dc, get_data(dc, timeout), get_stashes(dc, timeout))
    return r


@app.route('/', methods=['GET'])
def root():
    aggregated = list()
    pool = ThreadPool(len(dcs))
    aggregated = pool.map(get_agg_data, dcs)
    return render_template('data.html', dcs=dcs, data=aggregated, filter_data=get_filter_data(dcs, timeout), appcfg=appcfg)


@app.route('/filtered/<string:filters>', methods=['GET'])
def filtered(filters):
    aggregated = []
    for dc in dcs:
        if check_connection(dc):
            aggregated.append(agg_data(dc, get_data(dc, timeout), get_stashes(
                dc, timeout), get_clients(dc, timeout), filters))

    return render_template('data.html', dcs=dcs, data=aggregated, filter_data=get_filter_data(dcs, timeout), appcfg=appcfg)


@app.route('/show/<string:d>', methods=['GET'])
@app.route('/show/<string:d>/filtered/<string:filters>', methods=['GET'])
def showgrid(d, filters=None):
    data_detail = {}
    if dcs:
        for dc in dcs:
            if dc['name'] == d:
                if check_connection(dc):
                    if filters:
                        clients = get_clients(dc)
                    else:
                        clients = None

                    data_detail = agg_host_data(get_data(dc, timeout),
                                                get_stashes(dc, timeout), clients, filters)
                    if data_detail:
                        break
    else:
        abort(404)
    return render_template('detail.html', dc=dc, data=data_detail, filter_data=get_filter_data(dcs, timeout), appcfg=appcfg)


@app.route('/events/<string:d>')
@app.route('/events/<string:d>/filtered/<string:filters>')
def events(d, filters=''):
    results = []

    dc_found = False

    if dcs:
        for dc in dcs:
            if dc['name'] == d:
                dc_found = True
                if check_connection(dc):
                    results += get_events(dc, timeout, filters.split(','))
                break

    if dc_found is False:
        abort(404)

    results = sorted(results, lambda x, y: _cmp(
        x['check']['status'], y['check']['status']), reverse=True)

    return render_template('events.html', dc=dc, data=results, filter_data=get_filter_data(dcs, timeout), appcfg=appcfg)


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


@app.template_filter('color_for_event')
def color_for_event(event):
    if event['check']['name'] == 'keepalive':
        return 'purple'
    if event['check']['status'] == 1:
        return 'yellow'
    if event['check']['status'] == 2:
        return 'red'
    if event['check']['status'] == 0:
        return 'green'

    return 'gray'


@app.template_filter('icon_for_event')
def icon_for_event(event):
    if event['check']['name'] == 'keepalive':
        return 'arrow-circle-down'
    if event['check']['status'] == 1:
        return 'exclamation-circle'
    if event['check']['status'] == 2:
        return 'times-circle-o'
    if event['check']['status'] == 0:
        return 'check-circle'

    return 'question-circle'


if __name__ == '__main__':

    app.run(host='0.0.0.0',
            port=5000)
