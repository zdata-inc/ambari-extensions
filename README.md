File Explanations
-----------------
__GREENPLUM__  
Service definition Pivotal Greenplum that can be copied into an Ambari Stack directory.

__HAWQ__  
Service definition for Pivotal Hawq that can be copied into an Ambari Stack directory.

__vagrant__  
Contains bash scripts which provision the different nodes of the local cluster.

__Vagrantfile__  
Vagrantfile for bringing up a virtual Ambari cluster with Pivotal services to install.

Vagrant
-------

1. Requires the following plugins: vagrant-hostmanager

    ```
    vagrant plugin install vagrant-hostmanager
    ```

2. Create boxes

    ```
    vagrant up
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