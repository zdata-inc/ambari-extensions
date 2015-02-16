#!/bin/bash

# Setup repo
if find /vagrant/artifacts -name 'PHD*' -or -name 'PADS*' -quit &> /dev/null; then
    /vagrant/vagrant/setupRepo.sh
fi

sudo yum install -y ambari-server httpd

sudo service postgresql initdb
sudo ambari-server setup -s

sudo sh -c 'echo "client.api.port=8080" >> /etc/ambari-server/conf/ambari.properties'

sudo ambari-server start

sudo chkconfig postgresql on
sudo chkconfig ambari-server on

sudo sh -c 'echo "export SERVICES=/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/" >> ~/.bashrc'

echo 'URL: http://master.ambaricluster.local:8080'
echo 'Default username and password: admin/admin'
