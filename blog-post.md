# zData Ambari Stack with HAWQ Service

If you haven't heard about the [Apache Ambari project](http://ambari.apache.org/ "Apache Ambari Project") yet and you work with big data, you're missing out. Apache Ambari is a framework able to provision, manage, and monitor Apache Hadoop deployments. We will assume you have some familiarity with Ambari features and terminology. If you don't, don't sweat it! You can get caught up to speed from our [previous blog post](http://www.zdatainc.com/2014/11/apache-ambari-overview/).

We will be going over a project that we've been working on for the past few weeks: zData's Ambari Stack. The zData Ambari Stack defines a custom Ambari stack version that provides [Pivotal HAWQ](http://pivotal.io/big-data/pivotal-hawq) as a service. This means installing HAWQ has never been easier! You can quickly install HAWQ on a cluster to try out, benchmark, use, compare, or anything else. We'll be covering how we set up our stack definition, some design decisions we made, and finally how to download the zData stack and try it out yourself.

## What's a Stack Again?

An Ambari stack is a collection of services and how to install those services. Each service is defined with certain life-cycle commands (for example the life-cycle commands for a master are start, stop, install, configure, and status) and configuration information so Ambari can provision, manage, and monitor one or more services on a cluster. A stack also contains repository information used to find packages for installation, and meta information which describes that stack itself.

## About the zData Stack

The zData stack was created as a proof of concept, with the goal of giving the open source community an easy way to install HAWQ using Ambari. We wanted to start out with getting Pivotal HAWQ working in Ambari which has HDFS as a prerequisite. Instead of integrating [Pivotal HD](http://pivotal.io/big-data/pivotal-hd) into a new service and having that work first, we decided to inherit off of [Hortonwork's](http://hortonworks.com/hdp/) HDP 2.0.6 stack. Why? It works, it's tested, and it allowed us to get HAWQ working on HDFS as fast as possible. Stack inheritance allows the new stack version to install all its parent services and define new ones.  One of this project's longterm goals is to add Pivotal's HDFS / Hadoop distribution to the zData stack and define it as a new service.

Because we're currently inheriting from HDP 2.0.6, the zData stack is in actuality a stack version. It isn't possible to inherit services between stacks in Ambari, so our decision to use some of Hortonwork's services requires our stack version be a part of their stack. We define our stack version and copy it over to the HDP directory in the Ambari Server's /var/lib/ambari-server/resources/stacks directory so inheritance works properly.

## HAWQ as an Ambari Service

To integrate HAWQ into Ambari, we closely followed [manual HAWQ installation steps](http://pivotalhd.docs.pivotal.io/doc/2100/webhelp/index.html#topics/InstallingHAWQ.html) provided by Pivotal, tweaking them where necessary to be more Ambari friendly. To actually install HAWQ, you need to have downloaded Pivotal HD 2.1.0 and Pivotal HAWQ 1.2.1.0. These are usually distributed by Pivotal through their website and [can be downloaded from their website](https://network.pivotal.io/products/pivotal-hd). These distributions contain a number of rpms in an archive. To tie this into Ambari, we create a local repository server on the Ambari server that containes all of the packages. We simply extract both downloads into /var/www/html/phd, and run [createrepo](http://createrepo.baseurl.org/).  This is handled by the `build/setup-repo.sh` command when using vagrant. This allows us to be able to run `yum install hawq` and have yum take care of the dependencies. This simplifies Ambari's role in the actual installation of HAWQ quite a bit.

Actually creating the service definitions for Ambari requires quite a bit of custom Python; all of the service commands are written in Python. A great place to learn how to define a new service from scratch is from [this page in Ambari Wiki](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=38571133). It was a great help! Most of the steps in the installation guide for HAWQ are replicated in the installation command for the service. For instance, the gpssh-exkeys command is used to distribute keys to all of the servers in a cluster, allowing passwordless logins between them for a specific user.  Instead of using the command 'gpssh-exkeys' to accomplish this for the root user, we allow the Ambari registering step to take care of it (though we still use the command to distribute keys for the hawq user). Another example would be instead of copying the rpms that HAWQ requires to every server in the cluster, we instead have every server connect to the local repository defined on the Ambari server, which saves time and reduces complexity.

One significant part of any service is making it configurable. Ambari simplifies making services configurable by using XML files that contain a description of each configuration variable.  Every one of these variables is then made available in service's life-cycle commands. Almost every setting that goes into the gpinitsystem_config file was made configurable via Ambari. While adding a new service, or modifying an existing one, Ambari uses these XML files to create a user interface to modify the configurations.  The user can make changes or keep the defaults and save the various values. We set some default values but recommend that everyone review them. Finally, all of the configurations are written to a gpinitsystem_config file and used for the `gpinitsystem` command, which is all taken care of by our custom life-cycle commands for HAWQ.


## Hawq + Ambari = Awesome
Why is this so awesome? We believe this stack version will allow anyone to quickly provision a HAWQ cluster without having to learn or struggle through the installation settings. Ambari is extremely easy to install any service because of it's wizard-like steps. Anyone that's interested in trying out HAWQ on their own cluster can do so. No hardware? Set up an Ambari cluster in the cloud and then install HAWQ on it. Don't need good performance and just to learn HAWQ? Just create a virtual cluster with Virtualbox and Vagrant.

Ambari isn't just used to install HAWQ on a cluster, but manage and monitor it as well! It can keep track of any configuration changes and version them for easy rollback in case something breaks. Gone are the days of copying a config file with .old as a prefix or the date appended to it. Ambari also takes care of monitoring the cluster on your behalf with the Nagios and Ganglia services - two great open source projects for monitoring and metrics. When installing Nagios and Ganglia by default, they already have a lot of service checks and alerts in case something goes down. Service alerts can be easily extended to support HAWQ specific checks. Currently, Ambari is using the HAWQ status command to verify if the HAWQ master is up and if all the segments are up or not. 

Lastly, this is an evolving service and stack version. We can extend the HAWQ service in Ambari to support other non-standard commands that can be integrated into Ambari's web UI and api do things like run gpexpand, gpcheckperf, and gpcheck. We could also build up new nagios plugins for specific checks related to HAWQ. The API could even be used with an Ambari Blueprint to automate a HAWQ cluster install. 

## Future Plans
We're hoping the community takes a warming to this little project and contributes back bug fixes or feature requests to get the Ambari HAWQ service production ready. It has so much potential to make everything easier! We have started on a proof-of-concept service definition for Pivotal's Greenplum database as well and hope to get that into the stack definition down the road after some better code refactoring (I wrote it before knowing any Python so it's a hacked up mess). 

We hope to include other service definitions that make sense to the community and that aren't already out there. It would be great to add more service definitions and more packages that relate to the Hadoop ecosystem.

## Convinced to Try it Out?
Hopefully, we've convinced you that Ambari and HAWQ are awesome and how easy it is to jump in and try it out. You can find our stack version definition on Github.com <a href="https://github.com/zdata-inc/ambari-stack">here</a>. The README.md file and <a href="http://zdata-inc.github.io/ambari-stack/">our Github page</a> has all the information you need to get started!






