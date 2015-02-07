sudo yum install -y ambari-server httpd

sudo service postgresql initdb
sudo ambari-server setup -s

sudo sh -c 'echo "client.api.port=8080" >> /etc/ambari-server/conf/ambari.properties'

# Change to regex later...
if [ -f "/vagrant/artifacts/PHD-2.1.0.0-175.tar.gz" ]; then
  /vagrant/vagrant/setupRepo.sh
fi

sudo ambari-server start

sudo chkconfig postgresql on
sudo chkconfig ambari-server on

sudo sh -c 'echo "export SERVICES=/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/" >> ~/.bashrc'

echo 'URL: http://master.ambaricluster.local:8080'
echo 'Default username and password: admin/admin'
