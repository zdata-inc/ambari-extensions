---
layout: default
title: Getting Setup On Your Own Hardware
---

### Disclaimer
This article assumes the reader is using CentOS 6.5.

### Preconfiguration

Before getting started a bit of prep work is required.  Each host that is going to be a part of the cluster should have a FQDN (Fully Qualified Domain Name).  Each host should also have iptables stopped and disabled, SELinux disabled, and be configured with a common NTP server.

### Install Ambari (if necessary)

If Ambari hasn't yet been setup, now is the time to do it.  Ambari doesn't require many resources, so the service can be installed on a smaller host.

```sh
# As root

# Add the Ambari 1.7.x repository
wget http://public-repo-1.hortonworks.com/ambari/centos6/1.x/updates/1.7.0/ambari.repo -O /etc/yum.repos.d/ambari.repo
# Add EPEL repository
yum install epel-release

# Install Ambari server
yum install ambari-server

# Configure Postgres, a dependency of Ambari
service postgresql initdb

# Configure Ambari
ambari-server setup

# Start and enable the services
ambari-server start

chkconfig postgresql on
chkconfig ambari-server on
```

Alternatively you may follow <a href="https://cwiki.apache.org/confluence/display/AMBARI/Ambari+User+Guides" target="_blank">the installation steps provided in the Ambari Wiki</a>.

#### Configure local RPM repository

If a local RPM repository isn't already available where the Pivotal artifacts can be added for use during cluster creation, one will need to be setup.  This can be done on the Ambari host.  First the artifacts themselves need to be retrieved from [network.pivotal.io](https://network.pivotal.io), you will need an account if you don't have one already.

Download the following to `/tmp/artifacts`:

- [Pivotal HD 2.1 -> Pivotal HD 2.1.0](https://network.pivotal.io/products/pivotal-hd#/releases/2-1)
- [Pivotal HD 2.1 -> PHD 2.1.0: Pivotal HAWQ 1.2.1.0](https://network.pivotal.io/products/pivotal-hd#/releases/2-1)
- [4.3.5.0 Database Server -> Greenplum Database 4.3.5.0 for Red Hat Enterprise Linux 5 and 6](https://network.pivotal.io/products/pivotal-gpdb)

After those have been downloaded and moved to `/tmp/artifacts` on the Ambari server the local RPM repository can be created:

```sh
# As root

# Install the needed packages to create a local RPM repository
yum install httpd createrepo

# Create the local repository
mkdir -p /var/www/html/phd
tar -xvf /tmp/artifacts/PHD*.tar.gz -C /var/www/html/phd
tar -xvf /tmp/artifacts/PADS*.tar.gz -C /var/www/html/phd
createrepo /var/www/html/phd

# Start and enable the service
service httpd start
chkconfig httpd on
```

The repository should now be accessible at `http://<Ambari server FQDN>/phd`.  If this returns with a list of files in `/var/www/html/phd` then you're on the right track!


### Install zData stack

```sh
wget http://<latest release url>

tar -xzf zdata-ambari-stack-<version>.tar.gz
cd zdata-ambari-stack-<version>
make install
```

It is possible to customize where Ambari is installed, and what stack the zData stack version should be installed into with the environment variables `AMBARI_PATH` and `AMBARI_STACK` respectively.  For advanced users only, picking a stack other than HDP may break things.

```sh
AMBARI_PATH=/var/lib/non-standard-directory/resources/stacks AMBARI_STACK=PHD make install
```

### Start the Ambari Server
Start or restart the Ambari Server service:

```sh
sudo ambari-server restart
# Or
sudo ambari-server start
```

### Begin Install
You're all set to try the zData stack!  Point your URL to the fully qualified domain name of the Ambari Server (port 8080 by default), login, and setup a new cluster. When selecting a stack to use, you should see the zData stack definition listed.

Look through [Creating a Cluster]({{ site.baseurl }}/getting-setup/with-vagrant.html#creating-a-cluster) in the Vagrant setup guide for a more in depth guide to creating a cluster with Ambari, make sure to modify the Vagrant specific parts where necessary.