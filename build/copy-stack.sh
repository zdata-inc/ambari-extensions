#!/bin/bash
# Run on guest machines, replaces the cached zData stack with the newest one.

[ $EUID == 0 ] || exec sudo bash "$0" "$@" # Run as root

DESTINATION="/var/lib/ambari-agent/cache/stacks/PHD/9.9.9.zData/"

mkdir -p "$DESTINATION" 2> /dev/null
cp -R /vagrant/src/* "$DESTINATION"

find "$DESTINATION" -name "*.pyc" -delete
