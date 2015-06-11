#!/bin/bash
# Provisioning script for master machine managed by Vagrant.

# Include function definitions.
source /vagrant/build/functions.sh

# Choose which function to run to setup Ambari version.
## setupPivotalAmbari only works on zdata extensions 0.4 release branch
# setupPivotalAmbari /vagrant/artifacts/AMBARI-1.7.1-87-centos6.tar
# setupPivotalSoftwareSpecificRepo /vagrant/artifacts/PHD-UTILS-1.1.0.20-centos6.tar
# setupPivotalSoftwareSpecificRepo /vagrant/artifacts/PHD-3.0.0.0-249-centos6.tar
setupVanillaAmbari /vagrant/artifacts/ambari.repo
