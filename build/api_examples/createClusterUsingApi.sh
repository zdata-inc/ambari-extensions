#!/bin/bash
BLUEPRINT_PATH=/vagrant/build/api_examples/blueprint-example.json
CLUSTER_TEMPLATE_PATH=/vagrant/build/api_examples/cluster-template-example.json

# Make sure to install ambari-agent on all desired hosts and edit the hostname line in
# /etc/ambari-agent/conf/ambari-agent.ini to the Ambari Master's FQDN. 

# Command should list what's registered with server 
echo "Listing All Agents that have Registered with Server"
curl  -H "X-Requested-By: ambari" -X GET -u admin:admin http://master.ambaricluster.local:8080/api/v1/hosts

continue=
echo "Continue?"
read continue
if [ -z "$continue" ]; then
    echo "Exiting"
    exit
fi

# Post Blueprint and name it zdata
echo "Registering blueprint with server"
curl -d @$BLUEPRINT_PATH  -H "X-Requested-By: ambari" -X POST -u admin:admin http://master.ambaricluster.local:8080/api/v1/blueprints/zdata

# List Blueprint (make sure its there)
echo "Listing out blueprints registered with server"
curl -H "X-Requested-By: ambari" -X GET -u admin:admin http://master.ambaricluster.local:8080/api/v1/blueprints/

# Create Cluster using cluster template (different than blueprint)
echo "Spinning up cluster. Use API for watching status..."
curl -d @$CLUSTER_TEMPLATE_PATH -H "X-Requested-By: ambari" -X POST -u admin:admin http://master.ambaricluster.local:8080/api/v1/clusters/zdataCluster

echo "Watching status... Press control-c to stop..."
while :; do
    curl -H "X-Requested-By: ambari" -X GET -u admin:admin http://master.ambaricluster.local:8080/api/v1/clusters/zdataCluster/requests/1 | head -30
done
