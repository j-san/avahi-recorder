
[![Build Status](https://travis-ci.org/j-san/avahi-recorder.svg)](https://travis-ci.org/j-san/avahi-recorder)

Avahi Recorder
==============

Dynamic Zero Config DNS Server powered by Avahi.

Listen to Avahi and write DNS record for each discovered host on the lan. It allow Avahi to bind addresses for outsider subnetwork.

Install
-------

```
sudo pip2.7 install avahi-recorder
sudo avahi-recorder.py
# It will create  a DNS zone file in /etc/named/avahi-discover
# yum install bind dnsutils
# configure your dsn server
# enjoy :)
```

Develop
-------

```
virtualenv -p python2 env
env/bin/pip install -e .[dev]
env/bin/flake8 *.py
env/bin/avahi-recorder.py
```

TODOs
-----

- Configurable PARENT_DOMAIN, ZONE_FILE
- Example of working DNS config
- command line arguments
  - `domain`
  - `service-type`
  - `--permanent`

If you want some todos done, just [tweet me](https://twitter.com/j_sanp) :)

Licence
-------

**THE BEER-WARE LICENSE** (Revision 42):

Jonathan Sanchez wrote this software. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.
