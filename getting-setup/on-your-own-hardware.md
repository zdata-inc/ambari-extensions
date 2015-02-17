---
layout: default
title: Getting Setup On Your Own Hardware
---

### Overview

### Disclaimer
This article assumes the reader is using CentOS 6.5.

### Prerequisites
* All hosts should have FQDNs (fully qualified domain names)
* Anything else Ambari says your hosts should / shouldn't have.

### Setup Local Repository
##### Pick a Host
Pick a host that is accessible to all other hosts that will act as your local repository. We recommend using the same host as the one that will be used for the Ambari Server. Create a new directory called "phd" in your webroot directory. 
>mkdir -p /var/www/html/phd

##### Install Packages
As root, install or verify the following packages are insalled:
* httpd
* createrepo

>yum install -y httpd createrepo

##### Download Software from Pivotal
Download the Pivotal HD 2.1.0 and Pivotal HAWQ 1.2.1.0 from Pivotals website from [this address](https://network.pivotal.io/products/pivotal-hd). Copy these tar files to your repository host then untar them into /var/www/html/phd

##### Create the Repo
As root, cd to /var/www/html/phd and run createrepo .

>createrepo .

#### Start Webserver
Start up httpd and make sure httpd is ran after reboot:
>service httpd start

>chkconfig httpd on 

#### Verify Repo is Working
You don't need to create a .repo file. Ambari will do that for you during the installation process. Just make sure the webserver is actually working with a simple curl call.
>curl -L http://[your repository FQDN]/phd 

If this returns with a list of files in /var/www/html/phd then you're on the right track!

### Install Ambari Server
