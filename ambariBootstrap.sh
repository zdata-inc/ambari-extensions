#!/bin/bash
STABLE_REPO_URL=http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.6.1/ambari.repo
TRUNK_REPO_URL=http://s3.amazonaws.com/dev.hortonworks.com/ambari/centos6/1.x/updates/1.7.0.trunk/ambari.repo
AMBARI_REPO=$TRUNK_REPO_URL


PHD_TAR_PATH=/vagrant/PHD-2.0.1.0-148.tar
LOCAL_REPO_DIR=/var/www/html/phd/
PHD_DIR=PHD-2.0.1.0-148

#ssh-keygen -f /root/.ssh/id_rsa -N ""
#cat /root/.ssh/id_rsa.pub > /root/.ssh/authorized_keys

# Create RSA Keys
mkdir /root/.ssh
cp /vagrant/id_rsa /root/.ssh/.
cp /vagrant/id_rsa.pub /root/.ssh/authorized_keys
chmod 600 /root/.ssh/id_rsa

yum install -y openssl
yum update -y openssl
yum install -y httpd
#yum install -y createrepo
#mkdir -p $LOCAL_REPO_DIR
#tar -xvf $PHD_TAR_PATH -C $LOCAL_REPO_DIR
#createrepo $LOCAL_REPO_DIR/$PHD_DIR
wget $AMBARI_REPO
mv ambari.repo /etc/yum.repos.d/.

chkconfig iptables off
service iptables stop
setenforce 0
service ntpd stop
ntpdate pool.ntp.org
service ntpd start

yum install -y ambari-server
#> /etc/yum.repos.d/local.repo
#echo '[local]' >> /etc/yum.repos.d/local.repo
#echo 'name=CentOS-$releasever - local packages for $basearch' >> /etc/yum.repos.d/local.repo
#echo "baseurl=file://${LOCAL_REPO_DIR}${PHD_DIR}/" >> /etc/yum.repos.d/local.repo
#echo 'enabled=1' >> /etc/yum.repos.d/local.repo
#echo 'gpgcheck=0' >> /etc/yum.repos.d/local.repo
#echo 'protect=1' >> /etc/yum.repos.d/local.repo

#cp -r /vagrant/PHD /var/lib/ambari-server/resources/stacks/.
cp -r /vagrant/GREENPLUM /var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/
cp -r /vagrant/HAWQ /var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/ 
ambari-server setup -s
ambari-server start 
service httpd start
echo 'export SERVICES=/var/lib/ambari-server/resources/stacks/HDP/2.0.6/services/' >> /root/.bashrc
echo 10.0.0.11  node1.hadoop-cluster.com >> /etc/hosts
cat /etc/hosts | grep -i node | awk '{print $2}'
cat /root/.ssh/id_rsa
cp /vagrant/.vimrc /root/.vimrc
