sudo yum install -y ambari-server

sudo service postgresql initdb
sudo ambari-server setup -s

sudo sh -c 'echo "client.api.port=80" >> /etc/ambari-server/conf/ambari.properties'

sudo ambari-server start

sudo chkconfig postgresql on
sudo chkconfig ambari-server on

sudo sh -c 'echo "export SERVICES=/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/"" >> ~/.bashrc'

echo 'Default username and password: admin/admin'