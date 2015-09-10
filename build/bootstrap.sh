#!/bin/bash
## Provisioning script for all machines managed by Vagrant, run first.

# Include function definitions.
source /vagrant/build/functions.sh

# Default List of functions to run.
functionList=(
    "vagrantSetupHostsFile"
    "vagrantCreateSharedKeys"
    "installDesiredPackages"
    "setupNTPD"
    "disableFirewall"
    "removeMemoryLimitationOnUsers"
    "setSystemScheduling"
    "disableTHP"
    "disableSelinux"
    "configureSSH"
)

TYPE="$1"
FLAVOR="$2"

case "$FLAVOR" in
    'vanilla')
	if [[ "$TYPE" == "master" ]]; then
	    functionList+=('setupVanillaAmbari /vagrant/artifacts/ambari.repo')
	fi
	;;
    'pivotal')
	if [[ "$TYPE" == "master" ]]; then
	    functionList+=(
		'setupPivotalAmbari /vagrant/artifacts/AMBARI-1.7.1-87-centos6.tar'
		'setupPivotalSoftwareSpecificRepo /vagrant/artifacts/PHD-UTILS-1.1.0.20-centos6.tar'
		'setupPivotalSoftwareSpecificRepo /vagrant/artifacts/PHD-3.0.0.0-249-centos6.tar'
	    )
	fi
	;;
    *)
	echo "No flavor specified."
	;;
esac

for functionName in "${functionList[@]}"; do
	echo
	echo "Running $functionName"
	echo
	# Call function name.

	$functionName

	# Check return code.
 	if [ $? -ne 0 ]; then
	    echo "Function $functionName returned non-zero exit code!"
	fi
done
