---
layout: default
title: Creating a Cluster in Ambari
---

<br/>
You've got Ambari up, you have servers you want to provision, now what?  
Now you need to define a cluster in Ambari, and install the needed components on the servers.  

### Creating A Cluster

1. You'll need to visit the installation page for the Ambari server.  If you use the hostname scheme accompanied with the included vagrant scripts that url is [http://master.ambaricluster.local:8080](http://master.ambaricluster.local:8080).  

2. You'll need to login to Ambari.  By default the login is: admin / admin.  

3. After logging into a freshly install Ambari server, you should see the below screen.  Click on the 'Create a New Cluster TODO' button.

    TODO: IMAGE

4. First you'll need to select a stack, we recommend the 1.0.0.zData stack, as it's currently the only stack which can install HAWQ.

5. Next you'll need to input each of the machines to provision, as well as a private key which will allow you to login as root on each machine.  If you used vagrant to setup these machines their hostnames should be `slave0.ambaricluster.local`, `slave1.ambaricluster.local`, etc.; and the private key will be located in the project's root named private_key.

    After you click Next TODO, you'll see progress indicators showing the registration of the machines, and the installation of the Ambari agent.

    TODO: IMAGE

6. After registration of the machines has completed you'll be prompted to install services on them.  The smallest complete stack for HAWQ contains HDFS, Nagios, Zookeeper, Ganglia, and Hawq.  Select these and any other services you may want and proceed.

    TODO IMAGE

7. You'll now be asked to decide where to install what components.  For small installations it is recommended to put the master components on the Ambari server, and use the slaves for HDFS datanodes and HAWQ segments.  Larger deployments may distribute their components differently.

    TODO IMAGE

8. At this point you'll need to configure each of the components to be installed.  For our purposes of just deploy a small cluster to practice with the defaults are fine.  You'll need to input some information for Nagios and Hawq.

    For Nagios, you must input information to create an admin account, as well as an email for alerts to be sent ot.

    For Hawq, you must input at least the password for the hawq administration user and the url for the hdfs namenode.  If you're using vagrant that url will be: `hdfs://master.ambaricluster.local:8020` TODO.

    TODO IMAGE

9. Now we're installing!  If everything goes to plan you'll have a fully provisioned cluster in just a few minutes!

    TODO IMAGE

If you've made it this far you're ready to give your HAWQ cluster a test run!
TODO