# sensu-grid

Flask application to connect to a list of sensu-api servers and displays a grid of OK, WARNING, CRITICAL, DOWN and ACK'd alerts.

## features

- overview by data centre ( Name, OK, WARN, CRIT, DOWN, ACK )
- detail view by data centre ( Grid of hosts, color changes based on amount of alerting checks, 1 = yellow, > 1 = red, down = purple )
- Events view by data centre (Grid of events which are currently alerting/warning/unknown)
- filter by hosts' subscription/s ( Only shows matchin hosts' check results in overview and detail view)

## screenshots

Overview (DCs)

![sensu-grid overview screenshot](https://raw.githubusercontent.com/alex-leonhardt/sensu-grid/master/screenshots/screenshot_sensu-grid.png)

[More screenshots](SCREENSHOTS.md)

# faq

#### how can I filter by more than 1 value?

Amend the URL and add all the filters together as a comma-separated list, e.g.:
http://localhost:5000/filtered/aaa,bbb,ccc,ddd

#### what do the filters filter by ?

They filter based on the hosts' subscriptions, except in the Events view where they filter on all properties of the check and the host.

# docker

#### requirements

- docker (obviously)
- boot2docker (if you're on mac/windows)

#### build / run docker image

```
docker build -t name/sensu-grid:latest .
docker run -d -p 80:5000 name/sensu-grid:latest
```

# install / setup
_if you dont want to use docker_

### virtualenv

- Checkout this directory into ```/opt/sensu-grid```

```

virtualenv .
. bin/activate

```

### requirements

#### python requirements

Add via pip install or via your package management

- requests
- PyYAML
- Flask
- argparse
- gunicorn

### install requirements

- Install all required python libs first:

  ```

  pip install -r requirements.txt

  ```

### app user

- Create the app user:

  ```

  useradd -r sensu-grid

  ```

## run as a service

#### supervisord

- Install supervisord (```yum -y install supervisor```)
- Copy the provided config (```start-scripts/supervisord.conf```) file to ```/etc/supervisord.conf```

#### upstart

- Install upstart (```yum -y install upstart```)
- Copy the provided upstart config (```start-scripts/sensu-grid.conf```) file to ```/etc/init/```

## configuration

You should copy the ```conf/config.yaml.sample``` file to ```conf/config.yaml``` and edit as appropriate.

If you use username/password, ensure you set the appropriate permissions - e.g. ```chmod 640 conf/config.yaml``` and set the owner to ```sensu-grid``` which you'll be using to run this app.

### example config
```
---
dcs:
  -
    name: dev
    url: sensu-dev.domain.local
    port: 4567
    uchiwa: http://sensu-dev.domain.local:3000
  -
    name: stage
    url: sensu-stage.domain.local
    port: 4567
    user: apiuser
    password: apipassword

app:
  refresh: 60
  bg_color: #333333
  # This is a python requests layer timeout, as by default, it does not timeout
  requests_timeout: 10
  logging_level: info
```

## run locally / manually
(this requires you to install all the dependencies)


### local dev server

```
cd <checkout>
/usr/bin/python sensugrid.py
```

## healthcheck

a healthcheck is available at ```/healthcheck``` which returns json formatted text, which you can pipe into ```python -m json.tool```

example:
```
curl http://localhost:5000/healthcheck | python -m json.tool
```
