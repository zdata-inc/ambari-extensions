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
Follow the steps from the Ambari Wiki for directons on how to install the latest Ambari Server [at this address](https://cwiki.apache.org/confluence/display/AMBARI/Ambari+User+Guides).

### Clone zData Ambari Stack Repo 
Clone the zData Ambari Stack Repo on the Ambari Server. Install git if needed. 
>yum install -y git

>git clone (link)

cd into ambari-stack and copy the src directory to /var/lib/ambari-server/resources/stacks/HDP
>cd ambari-stack && cp -r src /var/lib/ambari-server/resources/stacks/HDP/.

### Start the Ambari Server
Start or restart the Ambari Server service by running the following as root:
>ambari-server restart|start

### Begin Install
You're all set to try the zData stack! Point your URL to the fully qualified domain name of the Ambari Server, login, and setup a new cluster. When selecting a stack to use, you should see the zData stack definition listed.

#### Change Local Repo Url
Select the custom stack definition and review the repo urls. Change the localhost entry to the FQDN of the Ambari Server.

#### Configure HAWQ and Finish Install
During the configuration portion of the install, you can change various settings for HAWQ. The HDFS url link and the hawq password will be required. Everything else has defaults but will need to be reviewed and can be edited to your desires.

### Use Hawq
After a successful install, you should be able to connect to HAWQ with the settings you configured. If you have some time and want to learn more about HAWQ, we recommend the HAWQ tutorials over at Pivotal's website located [at this address](http://pivotalhd.docs.pivotal.io/tutorial/getting-started/hawq.html).
