#!/bin/bash
# Provisioning script for master machine managed by Vagrant.

cd /tmp

/vagrant/build/setup-repo.sh

if [ -d /vagrant/artifacts/rpms ]; then
    rpm --replacepkgs --nosignature -i \
        /vagrant/artifacts/rpms/postgresql-libs-8.4.20-1.el6_5.x86_64.rpm \
        /vagrant/artifacts/rpms/postgresql-8.4.20-1.el6_5.x86_64.rpm \
        /vagrant/artifacts/rpms/postgresql-server-8.4.20-1.el6_5.x86_64.rpm \
        /vagrant/artifacts/rpms/ambari-server-1.7.0-209.noarch.rpm

    rpm --replacepkgs --nosignature -i \
        /vagrant/artifacts/rpms/ambari-agent-1.7.0-209.x86_64.rpm
else
    yum install -y ambari-server ambari-agent
fi

if [ -f /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz ]; then
    cp /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz /var/lib/ambari-server/resources/jdk-7u67-linux-x64.tar.gz
fi

if [ -f /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip ]; then 
    cp /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip /var/lib/ambari-server/resources/UnlimitedJCEPolicyJDK7.zip
fi

service postgresql initdb
ambari-server setup -s 

ambari-server start

chkconfig postgresql on
chkconfig ambari-server on

echo 'URL: http://master.ambaricluster.local:8080'
echo 'Default username and password: admin/admin'
