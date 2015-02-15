# AMBARI_REPO=http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.7.0/ambari.repo
AMBARI_REPO=http://s3.amazonaws.com/dev.hortonworks.com/ambari/centos6/1.x/updates/1.7.0.trunk/ambari.repo

yum install -y screen vim

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

# Change to regex later...
if find /vagrant/artifacts -name 'PHD*' -or -name 'PADS*' -quit &> /dev/null; then
  /vagrant/vagrant/setupRepo.sh
fi

umask 022

sudo yum install -y openssl ntp

sudo chkconfig iptables off
sudo service iptables stop

sudo sh -c 'echo 0 > /selinux/enforce'

sudo service ntpd stop
sudo ntpdate pool.ntp.org
sudo service ntpd start
sudo chkconfig ntpd on

if [ -f /vagrant/.vimrc ]; then
    sudo cp /vagrant/.vimrc /root/.vimrc
fi

# Fix for gotcha #1
sed -i "s;^127\.0\.0\.1\(.*\);127.0.0.1 localhost;" /etc/hosts