#!/bin/bash
## Provisioning script for all machines managed by Vagrant, run first.

cd /tmp
AMBARI_REPO=http://public-repo-1.hortonworks.com/ambari/centos6/2.x/updates/2.0.0/ambari.repo

yum install -y wget

if [ -d /vagrant/artifacts/rpms ]; then
    rpm --replacepkgs --nosignature -i \
        /vagrant/artifacts/rpms/screen-4.0.3-16.el6.x86_64.rpm

    rpm --replacepkgs --nosignature -U \
        /vagrant/artifacts/rpms/vim-common-7.2.411-1.8.el6.x86_64.rpm \
        /vagrant/artifacts/rpms/perl-version-0.77-136.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/perl-libs-5.10.1-136.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/perl-5.10.1-136.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/perl-Pod-Escapes-1.04-136.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/perl-Pod-Simple-3.13-136.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/perl-Module-Pluggable-3.90-136.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/gpm-libs-1.20.6-12.el6.x86_64.rpm \
        /vagrant/artifacts/rpms/vim-enhanced-7.2.411-1.8.el6.x86_64.rpm

    rpm --replacepkgs --nosignature -U /vagrant/artifacts/rpms/openssl-1.0.1e-30.el6_6.5.x86_64.rpm
    rpm --replacepkgs --nosignature -U /vagrant/artifacts/rpms/ntpdate-4.2.6p5-3.el6.centos.x86_64.rpm /vagrant/artifacts/rpms/ntp-4.2.6p5-3.el6.centos.x86_64.rpm
else
    yum install -y vim screen openssl ntp
fi

# Create shared keys
su - <<'EOF'
    if [ ! -f ~/.ssh ]; then
        mkdir ~/.ssh
    fi

    cat /vagrant/keys/private_key.pub >> ~/.ssh/authorized_keys
    cp /vagrant/keys/private_key ~/.ssh/id_rsa
    cp /vagrant/keys/private_key.pub ~/.ssh/id_rsa.pub
EOF

# Add EPEL repository
yum install -y epel-release

# Add ambari repository
if [ ! -f ambari.repo ]; then
    wget $AMBARI_REPO -q -O ambari.repo
    cp ambari.repo /etc/yum.repos.d/ambari.repo
fi

umask 022

chkconfig iptables off
service iptables stop

sed -i 's;SELINUX=.*;SELINUX=disabled;' /etc/selinux/config

service ntpd stop
ntpdate pool.ntp.org
service ntpd start
chkconfig ntpd on

# Fix for issue #1
sed -i "s;^127\.0\.0\.1\(.*\);127.0.0.1 localhost;" /etc/hosts
