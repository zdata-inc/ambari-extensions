---
layout: default
title: Getting Setup With Vagrant
---

### Windows Note:
The vagrant installation method is not tested on Windows, and most likely will not work without modifications.  You may be able to get the system to work by removing the `config.hostmanager.ip_resolver` lines, and manually setting the ips to their respective hostnames in the hostfiles of each machine.

### Prerequisites:

 - Vagrant
 - Vagrant Plugin: Hostmanager

    ```bash
    vagrant plugin install vagrant-hostmanager

    ```

### Installation


1. Run vagrant up to create and provision the virtual machines.  This step will install Ambari automatically.  
    __Warning:__ Each of the three virtual machines requires 4GB of RAM, only spin up one or two if RAM is limited!  

    ```bash
    vagrant up # Start master, slave0, and slave1
    vagrant up master slave0 # Start only master and slave0
    ```

2. 