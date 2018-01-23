import logging
import requests
import six

from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

from gridcheck import check_stash


LOGGER = logging.getLogger(__name__)


def _filter_data(timeout, dc):
    filter_data = list()
    r = None
    data = None
    LOGGER.debug("Retrieving filters for datacenter: {}".format(dc['name']))
    url = 'http://{0}:{1}/clients'.format(dc['url'], dc['port'])
    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']), timeout=timeout)
        else:
            r = requests.get(url, timeout=timeout)
        r.raise_for_status()
    except Exception as ex:
        LOGGER.error("Got exception while filtering on clients: {}".format(str(ex)))
        pass
    finally:
        if r:
            data = r.json()
            r.close()
        else:
            LOGGER.error("no reponse")

    if data:
        for i in data:
            for s in i['subscriptions']:
                if s not in filter_data:
                    filter_data.append(s)
    else:
        LOGGER.error("No response data")
    LOGGER.debug("Filter Retrieval for datacenter {} complete".format(dc['name']))
    return filter_data


def get_filter_data(dcs, timeout):
    aggregated = list()
    pool = ThreadPool(len(dcs))
    func = partial(_filter_data, timeout)
    aggregated = pool.map(func, dcs)
    if aggregated:
        assert type(aggregated) == list
        return aggregated

    return []


def get_data(dc, timeout):
    LOGGER.debug("Retrieving data for datacenter: {}".format(dc['name']))
    url = 'http://{0}:{1}/results'.format(dc['url'], dc['port'])
    data = None
    r = None
    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']), timeout=timeout)
        else:
            r = requests.get(url, timeout=timeout)
        r.raise_for_status()
    except Exception as ex:
        LOGGER.error("Got exception while retrieving data for dc: {} ex: {}".format(dc, str(ex)))
        pass
    finally:
        if r:
            data = r.json()
            r.close()
        else:
            LOGGER.error("no reponse")

    LOGGER.debug("Data Retrieval for datacenter {} complete".format(dc['name']))
    return data


def get_clients(dc, timeout):
    LOGGER.debug("Retrieving clients for datacenter: {}".format(dc['name']))
    url = 'http://{0}:{1}/clients'.format(dc['url'], dc['port'])
    data = None
    r = None

    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']), timeout=timeout)
            r.raise_for_status()
            data = r.json()
        else:
            r = requests.get(url, timeout=timeout)
            data = r.json()
    except Exception as ex:
        LOGGER.error("Got exception while retrieving clients for dc: {} ex: {}".format(dc, str(ex)))
        pass
    finally:
        if r:
            r.close()
        else:
            LOGGER.error("no reponse")

    LOGGER.debug("Client Retrieval for datacenter {} complete".format(dc['name']))
    return data


def get_stashes(dc, timeout):
    LOGGER.debug("Retrieving stashes for datacenter: {}".format(dc['name']))
    url = 'http://{0}:{1}/silenced'.format(dc['url'], dc['port'])
    data = None
    r = None
    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']), timeout=timeout)
            r.raise_for_status()
            data = r.json()
        else:
            r = requests.get(url, timeout=timeout)
            data = r.json()
    except Exception as ex:
        LOGGER.error("Got exception while retrieving stashes for dc: {} ex: {}".format(dc, str(ex)))
        pass
    finally:
        if r:
            r.close()
        else:
            LOGGER.error("no reponse")

    LOGGER.debug("Stash Retrieval for datacenter {} complete".format(dc['name']))
    return data


def filter_object(obj, search):
    if type(obj) == dict:
        for k, value in obj.iteritems():
            if filter_object(value, search):
                return True
    elif type(obj) == list:
        for value in obj:
            if filter_object(value, search):
                return True
    else:
        return six.u(search) in six.u(obj)

    return False


def filter_events(filters):
    def filter_event(event):
        for f in filters:
            if filter_object(event, f):
                return True
        return False

    return filter_event


def get_events(dc, timeout, filters=[]):
    LOGGER.debug("Retrieving events for datacenter: {}".format(dc['name']))
    url = 'http://{0}:{1}/events'.format(dc['url'], dc['port'])

    data = []
    r = None

    try:
        if 'user' and 'password' in dc:
            r = requests.get(url, auth=(dc['user'], dc['password']), timeout=timeout)
            r.raise_for_status()
            data = r.json()
        else:
            r = requests.get(url, timeout=timeout)
            data = r.json()
    except Exception as ex:
        LOGGER.error("Got exception while retrieving events for dc: {} ex: {}".format(dc, str(ex)))
        pass
    finally:
        if r:
            r.close()

    LOGGER.debug("Events Retrieval for datacenter {} complete".format(dc['name']))
    if len(filters) > 0:
        return filter(filter_events(filters), data)
    else:
        return data


def agg_data(dc, data, stashes, client_data=None, filters=None):
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
    _filtered = []

    if filters and len(filters) > 0:
        filters = filters.split(',')

    if filters is not None and client_data is not None:
        for c in client_data:
            for sub in c['subscriptions']:
                if sub in filters:
                    _filtered.append(c['name'])

    if data:
        for i in data:

            if len(_filtered) > 0:

                if i['client'] in _filtered:

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
                            # we cannot currently apply filters as keepalive checks do
                            # not have subscribers/subscriptions
                            down += 1
                        else:
                            ack += 1

            elif filters is None:

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
                        # we cannot currently apply filters as keepalive checks do not have subscribers/subscriptions
                        down += 1
                    else:
                        ack += 1

    return {"name": dc['name'], "ok": ok, "warning": warn, "critical": crit, "down": down, "ack": ack}


def agg_host_data(data, stashes, client_data=None, filters=None):
    """
    returns: a dict of {"hostname": [list,of,alert,statuses], "hostname2": [list,of,alert,statuses]}
    """

    _data = data
    _stashes = stashes
    _clients = client_data
    retdata = {}

    if filters and len(filters) > 0:
        filters = filters.split(',')

    if _clients is not None:
        for c in _clients:
            if filters and len(filters) > 0:
                for f in filters:
                    if f in c['subscriptions']:
                        _host = c['name']
                        retdata[_host] = []
                        break
            else:
                _host = c['name']
                retdata[_host] = []
    else:
        for check in _data:
            _host = check['client']
            retdata[_host] = []

    for check in _data:
        _host = check['client']
        if check['check']['status'] and check['check']['name'] != 'keepalive':
            if _host in retdata:
                if not check_stash(_stashes, _host, check['check']['name']):
                    retdata[_host].append(check['check']['status'])

        if check['check']['status'] and check['check']['name'] == 'keepalive':
            if _host in retdata:
                retdata[_host].append(-1)

    assert type(retdata) == dict

    return retdata
