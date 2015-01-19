#!/bin/bash
VAGRANT=/vagrant
RPM_DIR=$VAGRANT/rpms

# Disable SELinux
setenforce 0

# Disable iptables
chkconfig iptables off
service iptables stop
/etc/init.d/iptables stop

# Create RSA Keys
mkdir /root/.ssh
cp /vagrant/id_rsa /root/.ssh/.
cp /vagrant/id_rsa.pub /root/.ssh/authorized_keys

# Add Ambari Repo
wget http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.6.1/ambari.repo
mv ambari.repo /etc/yum.repos.d/.

# Start ntpd 
service ntpd start

# Edit Hosts File 
#sed -i -e 's/127.0.0.1.*$//g' -e 's/::1.*$//g' -e '/^$/d' /etc/hosts
echo 10.0.1.10	node0.hadoop-cluster.com >> /etc/hosts
echo 10.0.0.11  node1.hadoop-cluster.com >> /etc/hosts
