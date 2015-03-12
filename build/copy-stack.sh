#!/bin/bash
[ $EUID == 0 ] || exec sudo bash "$0" "$@"

mkdir -p /var/lib/ambari-agent/cache/stacks/HDP/9.9.9.zData 2> /dev/null
cp -R /vagrant/src/* /var/lib/ambari-agent/cache/stacks/HDP/9.9.9.zData