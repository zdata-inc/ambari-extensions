#!/bin/bash
# AMBARI_REPO=http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.7.0/ambari.repo
AMBARI_REPO=http://s3.amazonaws.com/dev.hortonworks.com/ambari/centos6/1.x/updates/1.7.0.trunk/ambari.repo

rpm --replacepkgs --nosignature -i \
  /vagrant/artifacts/rpms/screen-4.0.3-16.el6.x86_64.rpm \
  || yum install -y screen

rpm --replacepkgs --nosignature -U \
  /vagrant/artifacts/rpms/vim-common-7.2.411-1.8.el6.x86_64.rpm \
  /vagrant/artifacts/rpms/perl-version-0.77-136.el6_6.1.x86_64.rpm \
  /vagrant/artifacts/rpms/perl-libs-5.10.1-136.el6_6.1.x86_64.rpm \
  /vagrant/artifacts/rpms/perl-5.10.1-136.el6_6.1.x86_64.rpm \
  /vagrant/artifacts/rpms/perl-Pod-Escapes-1.04-136.el6_6.1.x86_64.rpm \
  /vagrant/artifacts/rpms/perl-Pod-Simple-3.13-136.el6_6.1.x86_64.rpm \
  /vagrant/artifacts/rpms/perl-Module-Pluggable-3.90-136.el6_6.1.x86_64.rpm \
  /vagrant/artifacts/rpms/gpm-libs-1.20.6-12.el6.x86_64.rpm \
  /vagrant/artifacts/rpms/vim-enhanced-7.2.411-1.8.el6.x86_64.rpm \
  || yum install -y vim

# Create shared RSA keys
sudo su - <<'EOF'
if [ ! -f ~/.ssh ]; then
    mkdir ~/.ssh
fi
sh -c 'cat /vagrant/private_key.pub >> ~/.ssh/authorized_keys'
sh -c 'cp /vagrant/private_key ~/.ssh/id_rsa'
sh -c 'cp /vagrant/private_key.pub ~/.ssh/id_rsa.pub'
EOF

# Add Epel repo
if [ ! -f epel-release-6-8.noarch.rpm ]; then
    wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    sudo rpm -Uvh epel-release-6*.rpm
fi

# Add ambari repo
if [ ! -f ambari.repo ]; then
    wget $AMBARI_REPO -q -O ambari.repo
    sudo cp ambari.repo /etc/yum.repos.d/ambari.repo
fi

umask 022

rpm --replacepkgs --nosignature -U \
  /vagrant/artifacts/rpms/openssl-1.0.1e-30.el6_6.5.x86_64.rpm \
  || sudo yum install -y openssl

rpm --replacepkgs --nosignature -U \
  /vagrant/artifacts/rpms/ntpdate-4.2.6p5-3.el6.centos.x86_64.rpm \
  /vagrant/artifacts/rpms/ntp-4.2.6p5-3.el6.centos.x86_64.rpm \
  || sudo yum install -y ntp

sudo chkconfig iptables off
sudo service iptables stop

sudo sed -i 's;SELINUX=.*;SELINUX=disabled;' /etc/selinux/config

sudo service ntpd stop
sudo ntpdate pool.ntp.org
sudo service ntpd start
sudo chkconfig ntpd on

if [ -f /vagrant/.vimrc ]; then
    sudo cp /vagrant/.vimrc /root/.vimrc
fi

# Fix for issue #1
sed -i "s;^127\.0\.0\.1\(.*\);127.0.0.1 localhost;" /etc/hosts
