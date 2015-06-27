Configuration Snippets
----------------------

The Sensu package creates a `/etc/sensu/config.json.example` file that
contains example config stanzas required for a minimal Sensu installation.

However, you may also break this monolithic config file up into smaller
pieces which often helps with config management systems such as Puppet or Chef.

Place JSON snippets in the `/etc/sensu/conf.d` directory. Files must have
a `.json` suffix.

Examples:

`/etc/sensu/conf.d/client.json`:

    {
      "client": {
        "name": "localhost",
        "address": "127.0.0.1",
        "subscriptions": [
          "test"
        ]
      }
    }

`/etc/sensu/conf.d/graphite_handler.json`:

    {
      "handlers": {
        "graphite": {
          "type": "tcp",
          "socket": {
            "host": "127.0.0.1",
            "port": 2003
          },
          "mutator": "only_check_output"
        }
      }
    }
