---
layout: default
title: Getting Setup With Vagrant
---

### Note Regarding Windows:
The vagrant installation method is not tested on Windows, and most likely will not work without modifications.  You may be able to get the system to work by removing the `config.hostmanager.ip_resolver` lines, and manually setting the ips to their respective hostnames in the hostfiles of each machine.

### Prerequisites:

 - Vagrant
 - Vagrant Plugin: Hostmanager

    ```bash
    vagrant plugin install vagrant-hostmanager

    ```

### Installation

1. Run ./build/up.sh to create and provision the virtual machines.  This step will install Ambari automatically.  
    __Warning:__ Each of the virtual machines requires 4GB of RAM, only spin up one or two if RAM is limited!  

    ```bash
    ./build/up.sh 0 # Start only master
    ./build/up.sh 1 # Start master and one slave
    ./build/up.sh 5 # Start master and five slaves
    ```

2. After all hosts have been provisioned, connect to the master at <a href="http://master.ambaricluster.local" target="_blank">http://master.ambaricluster.local</a>.

3. Next we'll want to go through [how to create a cluster with Ambari]({{ baseurl }}/getting-setup/creating-a-cluster-in-ambari.html).