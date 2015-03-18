zData Ambari Stack
==================
Ambari is a tool which makes provisioning, managing, and monitoring of Apache Hadoop deployments easy.  zData's stack builds atop Ambari to provide easy deployment and management of HAWQ, Chorus, and soon other Pivotal technologies.

[Visit the project's documentation for quick start guides and more information.](http://zdata-inc.github.io/ambari-stack)


Getting started with Vagrant
----------------------------

1. Requires the following plugins: vagrant-hostmanager

    ```
    vagrant plugin install vagrant-hostmanager
    vagrant plugin install vagrant-reload
    ```

2. Create boxes

    ```
    AMBARI_SLAVES=5 vagrant up # Bring up master, slave1, slave2, ..., slave5
    AMBARI_SLAVES=1 vagrant up # Bring up master and slave1
    AMBARI_SLAVES=0 vagrant up # Bring up just master
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

To install HAWQ you will need some files from Pivotal.  
You can find these files at https://network.pivotal.io/products/pivotal-hd.  Create an account if you don't have one already, and download `Pivotal HD 2.1.0` and `PHD 2.1.0: Pivotal HAWQ 1.2.1.0`.  Place the downloaded files in the artifacts folder located in the project root.