#!/bin/bash

# Setup repo
/vagrant/build/setup-repo.sh

sudo yum install -y ambari-server httpd

sudo service postgresql initdb
sudo ambari-server setup -s

sudo ambari-server start

sudo chkconfig postgresql on
sudo chkconfig ambari-server on

echo 'URL: http://master.ambaricluster.local:8080'
echo 'Default username and password: admin/admin'
