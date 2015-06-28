# sensu-grid

Flask application to connect to a list of sensu-api servers and displays a grid of OK, WARNING, CRITICAL, DOWN and ACK'd alerts.

## screenshots

Overview (DCs)

![sensu-grid overview screenshot](https://raw.githubusercontent.com/alex-leonhardt/sensu-grid/master/screenshots/screenshot_sensu-grid.png)

Detail (per DC)

![sensu-grid detail screenshot](https://raw.githubusercontent.com/alex-leonhardt/sensu-grid/master/screenshots/sensu-grid_detail.png)
![sensu-grid detail screenshot](https://raw.githubusercontent.com/alex-leonhardt/sensu-grid/master/screenshots/sensu-grid_detaiL-2.png)


## install / setup

- Install all required python libs first:

  ```
  pip install -r requirements.txt
  ```

- Create the app user:

  ```
  useradd -r sensu-grid
  ```

#### supervisord

- Install supervisord (```yum install supervisor -y```)
- Copy the provided config (```start-scripts/supervisord.conf```) file to ```/etc/supervisord.conf```
- Checkout this directory into ```/opt/sensu-grid```
- Amend config/paths as appropriate to where you've checked out this code

#### upstart

- Install upstart (```yum install upstart -y```)
- Copy the provided upstart config (```start-scripts/sensu-grid.conf```) file to ```/etc/init/```
- Checkout this directory into ```/opt/sensu-grid```
- Amend config/paths as appropriate to where you've checked out this code

## configuration

If you use usernames/passwords, ensure you set the appropriate permissions - e.g. ```chmod 640 config.yaml``` and set the owner to ```sensu-grid``` which you'll be using to run this app.

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

## run it

```
/usr/bin/python sensu-grid.py -c /opt/sensu-grid/config.yaml
```

#### docker

```
docker build -t name/sensu-grid:latest .
docker run -d -p 80:5000 name/sensu-grid:latest
```

#### options

| option | description                     |
|-------:|:--------------------------------|
| -h     | help                            |
| -d     | debug (!) dont do this in prod  |
| -c     | full path to configuration file |

## requirements

Add via pip install or via your package management

- requests
- PyYAML
- Flask
- argparse
