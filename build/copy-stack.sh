#!/bin/bash
[ $EUID == 0 ] || exec sudo bash "$0" "$@"

cp -R /vagrant/src/* /var/lib/ambari-agent/cache/stacks/HDP/9.9.9.zData