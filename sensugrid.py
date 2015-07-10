from flask import Flask
from flask import render_template
from flask import abort
import json
from reverseproxied import ReverseProxied
from griddata import *
from gridconfig import *

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

myconfig = ProdConfig
app.config.from_object(myconfig)
dcs = app.config['DCS']
appcfg = app.config['APPCFG']


@app.route('/', methods=['GET'])
def root():
    aggregated = []
    for dc in dcs:
        if check_connection(dc):
            aggregated.append(agg_data(dc, get_data(dc), get_stashes(dc)))

    return render_template('data.html', dcs=dcs, data=aggregated, appcfg=appcfg)


@app.route('/filtered/<string:subscriptions>', methods=['GET'])
def filtered(subscriptions):
    aggregated = []
    for dc in dcs:
        if check_connection(dc):
            aggregated.append(agg_data(dc, get_data(dc), get_stashes(dc), subscriptions))

    return render_template('data.html', dcs=dcs, data=aggregated, appcfg=appcfg)


@app.route('/show/<string:d>', methods=['GET'])
def showgrid(d):
    data_detail = []
    if dcs:
        for dc in dcs:
            if dc['name'] == d:
                if check_connection(dc):
                    data_detail = agg_host_data(get_data(dc), get_stashes(dc))
                    if data_detail:
                        break
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
