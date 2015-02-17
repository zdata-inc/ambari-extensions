---
layout: default
title: zData Ambari Stack
---

What is the zData Ambari Stack
------------------------------
Ambari is a tool which makes provisioning, managing, and monitoring of Apache Hadoop deployments easy.  This stack builds atop Ambari to provide easy deployment and management of HAWQ.

Getting Setup
-------------
We currently provide two options for getting started with zData's Ambari Stack.  

#### With Vagrant
The first option is to setup the entire cluster with [Vagrant](https://www.vagrantup.com/) either locally or remotely (using one of Vagrant's cloud plugins such as [Vagrant AWS](https://github.com/mitchellh/vagrant-aws) or [Vagrant DigitalOcean](https://github.com/smdahlen/vagrant-digitalocean)).  

[More instructions about how to install using Vagrant are available here.]({{ site.baseurl }}/getting-setup/with-vagrant.html)

#### With Your Own Ambari Cluster
The second option is to deploy the zData Ambari Stack onto an existing Ambari installation your own hardware.  There are limitations with this option though: the cluster must be running CentOS 6.5, and while there can be other services running outside Ambari it is not recommended, or supported.

[More instructions about how to install on your own Ambari cluster are available here.]({{ site.baseurl }}/getting-setup/on-your-own-hardware.html)