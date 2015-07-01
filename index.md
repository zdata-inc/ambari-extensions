---
layout: default
title: zData Ambari Extensions
---

What is the zData Ambari Extension Pack?
----------------------------------------

Ambari is an Apache sponsored project whose goal is to make provisioning, managing, and monitoring of Apache Hadoop and other distributed deployments easy. zData's new Ambari Extensions is built on top of Ambari and provides easy deployment of Pivotal Greenplum, Pivotal HAWQ, and [zData Chorus](http://www.zdatainc.com/zdata-chorus).

Getting Started with zData Ambari Extensions
--------------------------------------------

Currently there are two different ways to get started with zData Ambari Extensions.

#### With Vagrant
Setup your cluster with [Vagrant](https://www.vagrantup.com/) locally or remotely (using one of Vagrant's cloud plugins such as [Vagrant AWS](https://github.com/mitchellh/vagrant-aws)). This method is usually used for demonstrative and testing purposes, production environments should shy away from using this method.

[Furthur Vagrant installation instructions are available here.]({{ site.baseurl }}/getting-setup/with-vagrant.html)

#### With Your Own Ambari Cluster
Deploy the zData Ambari Extension Pack onto an existing Ambari installation using your own hardware. Please note that the cluster should be running CentOS 6, it is not recommended or supported to have other services running outside of Ambari.

[Further instructions on installation for your own Ambari cluster are available here.]({{ site.baseurl }}/getting-setup/on-your-own-hardware.html)

Licensing
---------
Ambari is an open source deployment tool, users must follow license agreements provided by Hortonworks and Pivotal software.

Ambari Server Bootstrap Script
------------------------------
This script is used to quickly provision a server with Ambari, including zData's Ambari Extensions.  
This script is needed to follow along with zData's Greenplum + Ambari on AWS in Minutes video

Download [Ambari Server Bootstrap](https://s3-us-west-2.amazonaws.com/zdata-ambari/artifacts/provisioning/aws/ambari-server-bootstrap.sh).
