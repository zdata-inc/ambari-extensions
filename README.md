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
    # OR
    vagrant up master
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

Retrieve Artifacts
------------------

Visit https://network.pivotal.io/products/pivotal-hd
Download "Pivotal HD 2.1.0"
Download "PHD 2.1.0: Pivotal HAWQ 1.2.1.0"


Gotchas
-------

#### 1  Remote Datanodes Cannot Connect to Namenode

__Symptoms:__
 - Remote datanodes will have the following in their logs when started.  

   ```
   INFO  ipc.Client (Client.java:handleConnectionFailure(783)) - Retrying connect to server: master.ambaricluster.local/172.28.128.3:8020. Already tried 0 time(s); retry policy is RetryUpToMaximumCountWithFixedSleep(maxRetries=50, sleepTime=1 SECONDS)
   ```

__Solutions:__
 - Make sure default hdfs url isn't set to localhost.  Setting to localhost will bind the listener to localhost, and not an ethernet interface, only allowing connections locally.
 - Verify in the /etc/hosts file that 127.0.0.1 is never associated with the hostname set for default.dfs.url.