This directory contains the following:

GREENPLUM			Service definition Pivotal Greenplum that can be copied into an Ambari Stack directory.
HAWQ				Service definition for Pivotal Hawq that can be copied into an Ambari Stack directory.
Vagrantfile			Vagrantfile for bringing up a virtual Ambari cluster with Pivotal services to install.
ambariBootstrap.sh		Simple bash script that vagrant calls to provision the Ambari Server and install the Ambari Server software.
globalBootstrap.sh		Simple bash script to provision other hosts in the cluster (excluding the Ambari Server).
id_rsa				Insecure private key.
id_rsa.pub			Corresponding public key.
