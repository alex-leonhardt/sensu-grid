# sensu-grid

Flask application to connect to a list of sensu-api servers and displays a grid of OK, WARNING, CRITICAL, DOWN and ACK'd alerts.

## screenshots

![sensu-grid screenshot](https://raw.githubusercontent.com/alex-leonhardt/sensu-grid/master/screenshots/screenshot_sensu-grid.png)

## example configuration
```
---
dcs:
  -
    name: dev
    url: sensu-dev.domain.local
    port: 4567
  -
    name: stage
    url: sensu-stage.domain.local
    port: 4567
    user: apiuser
    password: apipassword
    
app:
  refresh: 60
```

## run
```
python sensu-grid.py -c /full/path/to/example.yaml
```

#### options

| option | description                     |
|-------:|:--------------------------------|
| -h     | help                            |
| -d     | debug                           |
| -c     | full path to configuration file |

## requirements

Add via pip install or via your package management

- requests
- json
- yaml
- Flask
- re
- argparse

## todo

- add wsgi config
- either make it able to daemonize -or- use supervisord
