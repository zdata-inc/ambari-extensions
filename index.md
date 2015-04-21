---
layout: default
title: zData Ambari Stack
---

What is the zData Ambari Stack?
-------------------------------

Ambari is an Apache sponsored project whose goal is to make provisioning, managing, and monitoring of Apache Hadoop and other distributed deployments easy.  The zData stack builds on top of Ambari and provides easy deployment of Pivotal Greenplum, Pivotal HAWQ, and OpenChorus.


Getting Setup
-------------

Currently there are two different ways to get started with the zData Ambari stack.

#### With Vagrant
The first option is to setup the entire cluster with [Vagrant](https://www.vagrantup.com/) either locally or remotely (using one of Vagrant's cloud plugins such as [Vagrant AWS](https://github.com/mitchellh/vagrant-aws).

[More instructions about how to install using Vagrant are available here.]({{ site.baseurl }}/getting-setup/with-vagrant.html)

#### With Your Own Ambari Cluster
The second option is to deploy the zData Ambari stack onto an existing Ambari installation your own hardware.  There are limitations with this option though: the cluster should be running CentOS 6, and while there can be other services running outside Ambari it is not recommended, or supported.

[More instructions about how to install on your own Ambari cluster are available here.]({{ site.baseurl }}/getting-setup/on-your-own-hardware.html)
