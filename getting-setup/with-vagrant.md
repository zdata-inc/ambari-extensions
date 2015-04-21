---
layout: default
title: Getting Setup With Vagrant
---

### Note Regarding Windows:
The vagrant installation method is not tested on Windows, and most likely will not work without modifications.  You may be able to get the system to work by removing the `config.hostmanager.ip_resolver` lines, and manually setting the ips to their respective hostnames in the hostfiles of each machine.

### Prerequisites:

 - [Vagrant](https://www.vagrantup.com)
 - [Vagrant Plugin: Hostmanager](https://github.com/smdahlen/vagrant-hostmanager)
 - [Vagrant Plugin: Reload](https://github.com/aidanns/vagrant-reload)
 - [Vagrant Plugin: Triggers](https://github.com/emyl/vagrant-triggers)
 - [Vagrant Plugin: AWS](https://github.com/mitchellh/vagrant-aws) (optional)

    ```sh
    vagrant plugin install vagrant-hostmanager
    vagrant plugin install vagrant-reload
    vagrant plugin install vagrant-triggers

    vagrant plugin install vagrant-aws # To provision on AWS
    ```

### Installation

1. First you will need to retrieve certain artifacts from Pivotal.  Visit https://network.pivotal.io/products/pivotal-hd, create an account if you don't have one already.

2. Next download the following to the artifacts directory:
    - [Pivotal HD 2.1.0](https://network.pivotal.io/products/pivotal-hd#/releases/2-1)
    - [PHD 2.1.0: Pivotal HAWQ 1.2.1.0](https://network.pivotal.io/products/pivotal-hd#/releases/2-1)
    - [4.3.5.0 Database Server -> Greenplum Database 4.3.5.0 for Red Hat Enterprise Linux 5 and 6](https://network.pivotal.io/products/pivotal-gpdb)

3. Run `vagrant up` to create and provision the virtual machines.  This step will install Ambari automatically.  
    __Warning:__ Each of the virtual machines requires 4GB of RAM, only spin up one or two if RAM is limited!  

    ```sh
    AMBARI_SLAVES=0 vagrant up # Start only master
    AMBARI_SLAVES=1 vagrant up # Start master and one slave
    AMBARI_SLAVES=5 vagrant up # Start master and five slaves
    ```

2. After all hosts have been provisioned, connect to the master at <a href="http://master.ambaricluster.local:8080" target="_blank">http://master.ambaricluster.local:8080</a>.


Creating A Cluster
------------------

You've got Ambari up, you have servers you want to provision, now what?  
Now you need to define a cluster in Ambari, and install the needed components on the servers.  

1. First you'll need to access the Ambari web application.  If you use the hostname scheme accompanied with the included vagrant scripts that url is <a href="http://master.ambaricluster.local:8080" target="_blank">http://master.ambaricluster.local:8080</a>.  

2. Next you'll need to login to Ambari.  The default login is: admin / admin.  

3. After logging into a freshly install Ambari server, you should see a screen which will allow you to configure users/groups or begin a cluster installation.  Click on the 'Launch Install Wizard' button to begin configuring the cluster.

4. First you'll need to name your cluster and select its stack.  The name of the stack can be anything; for the stack we recommend 1.0.0.zData, as it's currently the only stack which can install Greenplum and HAWQ.

    Next you will need to toggle down the 'Advanced Repository Options', and uncheck suse11.  You will also want to change the `Local-PHD-Repo` to the local repository containing Pivotal's PHD and PADS rpms.  For vagrant installations the creation of this repository is automatically done during provisioning by the [setup-repo.sh script](https://github.com/zdata-inc/ambari-stack/blob/master/build/setup-repo.sh) so the Ambari server's domain can be used here (which is `http://master.ambaricluster.local` by default).

5. Next you'll need to input each of the machines to provision, as well as a private key which will allow you to login as root on each machine.  Vagrant configures the hostnames automatically to be `master.ambaricluster.local`, `slave1.ambaricluster.local`, `slave2.ambaricluster.local`, etc., and the private key will be located in `keys/private_key` relative to the project root.

    Normally you would provision the same server you have Ambari installed on, but because of the limited number of virtual machines that can be run at a time we'll use the master host as well as the slaves for the cluster.  After you click Next, you'll see progress indicators showing the registration of the machines, and the installation of the Ambari agents.

6. After registration has completed you will be prompted to install services on each of the machines.  The smallest complete stack for HAWQ contains HDFS, Zookeeper, and HAWQ.  You can install Greenplum by choosing just the Greenplum package.  You should also install Nagios and Ganglia, or Ambari won't be able to function fully.  Proceed after selecting all the services you want on your cluster.

7. You'll now be asked to decide where to install what components.  For small installations it is recommended to put the master components on the Ambari server, and use the slaves for datanodes and segments.  Larger deployments may distribute their components differently.

8. At this point you'll need to configure each of the components to be installed.  For our purposes of just deploy a small cluster to practice with the defaults are fine.  You'll need to input some information for Nagios, HAWQ, and/or Greenplum.

    For Nagios, you must input information to create an admin account, as well as an email for alerts to be sent to.

    For HAWQ, you must input at least the password for the HAWQ administration user and the url for the hdfs namenode.  With Vagrant that url will be: `hdfs://master.ambaricluster.local:8020`.

    For Greenplum, you must accept the license agreement, input a admin user password, and give a path to the location of the Greenplum installation zip archive (the one downloaded in installation's step 2).  The archive's path should be `/vagrant/artifacts/{GreenplumArchiveName}.zip` for the master node.

9. Now we're installing!  If everything goes to plan you'll have a fully provisioned cluster in just a few minutes!

If you've made it this far you're ready to give your HAWQ cluster a test run!