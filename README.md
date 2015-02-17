zData Ambari Stack
==================
Ambari is a tool which makes provisioning, managing, and monitoring of Apache Hadoop deployments easy.  zData's stack builds atop Ambari to provide easy deployment and management of HAWQ, Chorus, and soon other Pivotal technologies.

[Visit the project's documentation for quick start guides and more information.](http://zdata-inc.github.io/ambari-stack)


Getting started with Vagrant
----------------------------

1. Requires the following plugins: vagrant-hostmanager

    ```
    vagrant plugin install vagrant-hostmanager
    ```

2. Create boxes

    ```
    ./build/up.sh 5 # Bring up master, slave1, slave2, ..., slave5
    ./build/up.sh 1 # Bring up master and slave1
    ./build/up.sh 0 # Just bring up master
    ```

3. Connect, vms created: master, slave0, slave1
    
    ```
    master.ambaricluster.local
    slave0.ambaricluster.local
    slave1.ambaricluster.local

    vagrant ssh master
    vagrant ssh slave0
    vagrant ssh slave1
    ```

More information about getting started with Ambari using vagrant [is available here](http://zdata-inc.github.io/ambari-stack/getting-setup/with-vagrant.html).

Retrieve Artifacts
------------------

Visit https://network.pivotal.io/products/pivotal-hd
Download "Pivotal HD 2.1.0"
Download "PHD 2.1.0: Pivotal HAWQ 1.2.1.0"