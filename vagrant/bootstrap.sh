STABLE_REPO_URL=http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.6.1/ambari.repo
TRUNK_REPO_URL=http://s3.amazonaws.com/dev.hortonworks.com/ambari/centos6/1.x/updates/1.7.0.trunk/ambari.repo
AMBARI_REPO=$TRUNK_REPO_URL

# Create shared RSA keys
sudo su - <<'EOF'
if [ ! -f ~/.ssh ]; then
    mkdir ~/.ssh
fi
sh -c 'cat /vagrant/private_key.pub >> ~/.ssh/authorized_keys'
EOF

# Add ambari repo
if [ ! -f ambari.repo ]; then
    wget $AMBARI_REPO -q -O ambari.repo
    sudo cp ambari.repo /etc/yum.repos.d/ambari.repo
fi

umask 022
sudo yum install -y epel-release openssl ntp

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