#!/bin/bash
[ $EUID == 0 ] || exec sudo bash "$0" "$@"

cp -R /vagrant/1.0.0.zData/ /var/lib/ambari-agent/cache/stacks/HDP/