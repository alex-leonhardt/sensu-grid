# sensu-grid

Flask application to connect to a list of sensu-api servers and displays a grid of OK, WARNING, CRITICAL, DOWN and ACK'd alerts.

## Features

- overview by data centre ( Name, OK, WARN, CRIT, DOWN, ACK )
- detail view by data centre ( Grid of hosts, color changes based on amount of alerting checks, 1 = yellow, > 1 = red, down = purple )

- filter by hosts' subscription/s ( Only shows matchin hosts' check results in overview and detail view)

## screenshots

Overview (DCs)

![sensu-grid overview screenshot](https://raw.githubusercontent.com/alex-leonhardt/sensu-grid/master/screenshots/screenshot_sensu-grid.png)

[More screenshots](SCREENSHOTS.md)

## FAQ

#### How can I filter by more than 1 subscription ? 

Amend the URL and add all the subscriptions together as a comma-separated list, e.g.: 
http://localhost:5000/filtered/aaa,bbb,ccc,ddd

#### What do the filters filter by ? 

They filter based on the hosts' subscriptions.


## install / setup (if you dont want to use docker)

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

### run as a service

#### supervisord

- Install supervisord (```yum -y install supervisor```)
- Copy the provided config (```start-scripts/supervisord.conf```) file to ```/etc/supervisord.conf```

#### upstart

- Install upstart (```yum -y install upstart```)
- Copy the provided upstart config (```start-scripts/sensu-grid.conf```) file to ```/etc/init/```

## configuration

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
```

## run locally / manually
(this requires you to install all the dependencies)


### local dev server

```
cd <checkout>
/usr/bin/python sensugrid.py
```

### docker

#### requirements

- docker (obviously)
- boot2docker (if you're on mac/windows)

#### build / run docker image

```
docker build -t name/sensu-grid:latest .
docker run -d -p 80:5000 name/sensu-grid:latest
```

