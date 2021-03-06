#!/usr/bin/env ambari-python-wrap
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import os
from math import ceil

from stack_advisor import DefaultStackAdvisor


class zData999StackAdvisor(DefaultStackAdvisor):
    def recommendComponentLayout(self, services, hosts):

        hosts_to_groups = {
            'gp-master': [],
            'gp-segments': []
        }

        groups_to_components = {
            'gp-master': ['GREENPLUM_MASTER', 'GREENPLUM_CLIENT'],
            'gp-segments': ['GREENPLUM_SLAVE', 'GREENPLUM_CLIENT']
        }


        # Add hosts to groups
        for host in [host['Hosts'] for host in hosts['items']]:
            if any(s in host['host_name'] for s in ['smdw', 'standby']):
                hosts_to_groups['gp-standby'].append(host)
            elif any(s in host['host_name'] for s in ['mdw', 'master']):
                hosts_to_groups['gp-master'].append(host)
            elif any(s in host['host_name'] for s in ['sdw', 'segment', 'slave']):
                hosts_to_groups['gp-segments'].append(host)


        # Generate expected output
        recommended_layout = {}

        recommended_layout['hosts'] = [
            host['host_name']
            for group, hosts in hosts_to_groups.iteritems()
            for host in hosts
        ]

        recommended_layout['services'] = ['GREENPLUM']
        recommended_layout['Versions'] = {"stack_name": "zData", "stack_version": "9.9.9"}

        recommended_layout['recommendations'] = {}
        recommended_layout['recommendations']['blueprint'] = {'host_groups': []}

        for group, components in groups_to_components.iteritems():
            formatted_components = [{'name': component} for component in components]

            recommended_layout['recommendations']['blueprint']['host_groups'].append({
                'name': group,
                'components': formatted_components
            })

        recommended_layout['recommendations']['blueprint_cluster_binding'] = {'host_groups': []}

        for group, hosts in hosts_to_groups.iteritems():
            # pprint(hosts)
            formatted_hosts = [{'fqdn': host['host_name']} for host in hosts]

            recommended_layout['recommendations']['blueprint_cluster_binding']['host_groups'].append({
                'name': group,
                'hosts': formatted_hosts
            })

        return recommended_layout


    def getComponentLayoutValidations(self, services, hosts):
        """Returns array of Validation objects about issues with hostnames components assigned to"""
        items = []

        # Validating NAMENODE and SECONDARY_NAMENODE are on different hosts if possible
        hostsList = [host["Hosts"]["host_name"] for host in hosts["items"]]
        hostsCount = len(hostsList)

        componentsListList = [service["components"] for service in services["services"]]
        componentsList = [item for sublist in componentsListList for item in sublist]
        nameNodeHosts = [component["StackServiceComponents"]["hostnames"]
                         for component in componentsList if component["StackServiceComponents"]["component_name"] == "NAMENODE"]
        secondaryNameNodeHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component[
            "StackServiceComponents"]["component_name"] == "SECONDARY_NAMENODE"]

        # Validating cardinality
        for component in componentsList:
            if component["StackServiceComponents"]["cardinality"] is not None:
                componentName = component["StackServiceComponents"]["component_name"]
                componentDisplayName = component["StackServiceComponents"]["display_name"]
                componentHostsCount = 0
                if component["StackServiceComponents"]["hostnames"] is not None:
                    componentHostsCount = len(component["StackServiceComponents"]["hostnames"])
                cardinality = str(component["StackServiceComponents"]["cardinality"])
                # cardinality types: null, 1+, 1-2, 1, ALL
                message = None
                if "+" in cardinality:
                    hostsMin = int(cardinality[:-1])
                    if componentHostsCount < hostsMin:
                        message = "At least {0} {1} components should be installed in cluster.".format(
                            hostsMin, componentDisplayName)
                elif "-" in cardinality:
                    nums = cardinality.split("-")
                    hostsMin = int(nums[0])
                    hostsMax = int(nums[1])
                    if componentHostsCount > hostsMax or componentHostsCount < hostsMin:
                        message = "Between {0} and {1} {2} components should be installed in cluster.".format(
                            hostsMin, hostsMax, componentDisplayName)
                elif "ALL" == cardinality:
                    if componentHostsCount != hostsCount:
                        message = "{0} component should be installed on all hosts in cluster.".format(
                            componentDisplayName)
                else:
                    if componentHostsCount != int(cardinality):
                        message = "Exactly {0} {1} components should be installed in cluster.".format(
                            int(cardinality), componentDisplayName)

                if message is not None:
                    items.append(
                        {"type": 'host-component', "level": 'ERROR', "message": message, "component-name": componentName})

        # Validating host-usage
        usedHostsListList = [component["StackServiceComponents"]["hostnames"]
                             for component in componentsList if not self.isComponentNotValuable(component)]
        usedHostsList = [item for sublist in usedHostsListList for item in sublist]
        nonUsedHostsList = [item for item in hostsList if item not in usedHostsList]
        for host in nonUsedHostsList:
            items.append({"type": 'host-component', "level": 'ERROR', "message": 'Host is not used', "host": str(host)})

        return items

    def getServiceConfigurationRecommenderDict(self):
        return {
            "GREENPLUM": self.recommendGreenplumConfigurations,
            "YARN": self.recommendYARNConfigurations,
            "MAPREDUCE2": self.recommendMapReduce2Configurations,
            "HDFS": self.recommendHDFSConfigurations,
            "HBASE": self.recommendHbaseEnvConfigurations,
            "AMBARI_METRICS": self.recommendAmsConfigurations,
        }

    def putProperty(self, config, configType):
        if configType not in config or "properties" not in config[configType]:
            config[configType] = {"properties": {}}

        def appendProperty(key, value):
            config[configType]["properties"][key] = str(value)
        return appendProperty

    def recommendGreenplumConfigurations(self, configurations, clusterData, services, hosts):
        putGreenplumProperty = self.putProperty(configurations, 'greenplum-env')

        putGreenplumProperty('master_port', '5432' if not component_on_ambari(services, 'GREENPLUM_MASTER') else '6543')
        putGreenplumProperty('segments_per_node', max(int(clusterData['cpu']), 2))

    def recommendYARNConfigurations(self, configurations, clusterData, services, hosts):
        putYarnProperty = self.putProperty(configurations, "yarn-site")
        putYarnEnvProperty = self.putProperty(configurations, "yarn-env")
        putYarnProperty('yarn.nodemanager.resource.memory-mb',
                        int(round(clusterData['containers'] * clusterData['ramPerContainer'])))
        putYarnProperty('yarn.scheduler.minimum-allocation-mb', int(clusterData['ramPerContainer']))
        putYarnProperty('yarn.scheduler.maximum-allocation-mb',
                        int(round(clusterData['containers'] * clusterData['ramPerContainer'])))
        putYarnEnvProperty('min_user_id', self.get_system_min_uid())

    def recommendMapReduce2Configurations(self, configurations, clusterData, services, hosts):
        putMapredProperty = self.putProperty(configurations, "mapred-site")
        putMapredProperty('yarn.app.mapreduce.am.resource.mb', int(clusterData['amMemory']))
        putMapredProperty('yarn.app.mapreduce.am.command-opts', "-Xmx" +
                          str(int(round(0.8 * clusterData['amMemory']))) + "m")
        putMapredProperty('mapreduce.map.memory.mb', clusterData['mapMemory'])
        putMapredProperty('mapreduce.reduce.memory.mb', int(clusterData['reduceMemory']))
        putMapredProperty('mapreduce.map.java.opts', "-Xmx" + str(int(round(0.8 * clusterData['mapMemory']))) + "m")
        putMapredProperty(
            'mapreduce.reduce.java.opts', "-Xmx" + str(int(round(0.8 * clusterData['reduceMemory']))) + "m")
        putMapredProperty('mapreduce.task.io.sort.mb', min(int(round(0.4 * clusterData['mapMemory'])), 1024))

    def recommendHDFSConfigurations(self, configurations, clusterData, services, hosts):
        putHDFSProperty = self.putProperty(configurations, "hadoop-env")
        putHDFSProperty('namenode_heapsize', max(int(clusterData['totalAvailableRam'] / 2), 1024))
        putHDFSProperty = self.putProperty(configurations, "hadoop-env")
        putHDFSProperty('namenode_opt_newsize', max(int(clusterData['totalAvailableRam'] / 8), 128))
        putHDFSProperty = self.putProperty(configurations, "hadoop-env")
        putHDFSProperty('namenode_opt_maxnewsize', max(int(clusterData['totalAvailableRam'] / 8), 256))

    def recommendHbaseEnvConfigurations(self, configurations, clusterData, services, hosts):
        putHbaseProperty = self.putProperty(configurations, "hbase-env")
        putHbaseProperty('hbase_regionserver_heapsize', int(clusterData['hbaseRam']) * 1024)
        putHbaseProperty('hbase_master_heapsize', int(clusterData['hbaseRam']) * 1024)

    def recommendAmsConfigurations(self, configurations, clusterData, services, hosts):
        putAmsEnvProperty = self.putProperty(configurations, "ams-env")
        putAmsEnvProperty = self.putProperty(configurations, "ams-env")
        putAmsHbaseSiteProperty = self.putProperty(configurations, "ams-hbase-site")
        putTimelineServiceProperty = self.putProperty(configurations, "ams-site")
        putHbaseEnvProperty = self.putProperty(configurations, "ams-hbase-env")

        amsCollectorHosts = self.getComponentHostNames(services, "AMBARI_METRICS", "METRICS_COLLECTOR")
        putHbaseEnvProperty("hbase_regionserver_heapsize", "1024m")
        # blockCache = 0.3, memstore = 0.35, phoenix-server = 0.15, phoenix-client = 0.25
        putAmsHbaseSiteProperty("hfile.block.cache.size", 0.3)
        putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.upperLimit", 0.35)
        putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.lowerLimit", 0.3)
        putTimelineServiceProperty("timeline.metrics.host.aggregator.ttl", 86400)

        # TODO recommend configuration for multiple AMBARI_METRICS collectors
        if len(amsCollectorHosts) > 1:
            pass
        else:
            totalHostsCount = len(hosts["items"])
            # blockCache = 0.3, memstore = 0.3, phoenix-server = 0.2, phoenix-client = 0.3
            if totalHostsCount >= 400:
                putHbaseEnvProperty("hbase_master_heapsize", "12288m")
                putAmsEnvProperty("metrics_collector_heapsize", "8192m")
                putAmsHbaseSiteProperty("hbase.regionserver.handler.count", 60)
                putAmsHbaseSiteProperty("hbase.regionserver.hlog.blocksize", 134217728)
                putAmsHbaseSiteProperty("hbase.regionserver.maxlogs", 64)
                putAmsHbaseSiteProperty("hbase.hregion.memstore.flush.size", 268435456)
                putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.upperLimit", 0.3)
                putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.lowerLimit", 0.25)
                putAmsHbaseSiteProperty("phoenix.query.maxGlobalMemoryPercentage", 20)
                putTimelineServiceProperty("phoenix.query.maxGlobalMemoryPercentage", 30)
                putHbaseEnvProperty("hbase_master_xmn_size", "512m")
            elif totalHostsCount >= 100:
                putHbaseEnvProperty("hbase_master_heapsize", "6144m")
                putAmsEnvProperty("metrics_collector_heapsize", "4096m")
                putAmsHbaseSiteProperty("hbase.regionserver.handler.count", 60)
                putAmsHbaseSiteProperty("hbase.regionserver.hlog.blocksize", 134217728)
                putAmsHbaseSiteProperty("hbase.regionserver.maxlogs", 64)
                putAmsHbaseSiteProperty("hbase.hregion.memstore.flush.size", 268435456)
                putHbaseEnvProperty("hbase_master_xmn_size", "512m")
            elif totalHostsCount >= 50:
                putHbaseEnvProperty("hbase_master_heapsize", "2048m")
                putAmsEnvProperty("metrics_collector_heapsize", "2048m")
                putHbaseEnvProperty("hbase_master_xmn_size", "256m")
            else:
                putHbaseEnvProperty("hbase_master_heapsize", "1024m")
                putAmsEnvProperty("metrics_collector_heapsize", "512m")
                putHbaseEnvProperty("hbase_master_xmn_size", "128m")

    def getConfigurationClusterSummary(self, servicesList, hosts, components):

        hBaseInstalled = False
        if 'HBASE' in servicesList:
            hBaseInstalled = True

        cluster = {
            "cpu": 0,
            "disk": 0,
            "ram": 0,
            "hBaseInstalled": hBaseInstalled,
            "components": components
        }

        if len(hosts["items"]) > 0:
            host = hosts["items"][0]["Hosts"]
            cluster["cpu"] = host["cpu_count"]
            cluster["disk"] = len(host["disk_info"])
            cluster["ram"] = int(host["total_mem"] / (1024 * 1024))

        ramRecommendations = [
            {"os": 1, "hbase": 1},
            {"os": 2, "hbase": 1},
            {"os": 2, "hbase": 2},
            {"os": 4, "hbase": 4},
            {"os": 6, "hbase": 8},
            {"os": 8, "hbase": 8},
            {"os": 8, "hbase": 8},
            {"os": 12, "hbase": 16},
            {"os": 24, "hbase": 24},
            {"os": 32, "hbase": 32},
            {"os": 64, "hbase": 64}
        ]
        index = {
            cluster["ram"] <= 4: 0,
            4 < cluster["ram"] <= 8: 1,
            8 < cluster["ram"] <= 16: 2,
            16 < cluster["ram"] <= 24: 3,
            24 < cluster["ram"] <= 48: 4,
            48 < cluster["ram"] <= 64: 5,
            64 < cluster["ram"] <= 72: 6,
            72 < cluster["ram"] <= 96: 7,
            96 < cluster["ram"] <= 128: 8,
            128 < cluster["ram"] <= 256: 9,
            256 < cluster["ram"]: 10
        }[1]
        cluster["reservedRam"] = ramRecommendations[index]["os"]
        cluster["hbaseRam"] = ramRecommendations[index]["hbase"]

        cluster["minContainerSize"] = {
            cluster["ram"] <= 4: 256,
            4 < cluster["ram"] <= 8: 512,
            8 < cluster["ram"] <= 24: 1024,
            24 < cluster["ram"]: 2048
        }[1]

        totalAvailableRam = cluster["ram"] - cluster["reservedRam"]
        if cluster["hBaseInstalled"]:
            totalAvailableRam -= cluster["hbaseRam"]
        cluster["totalAvailableRam"] = max(2048, totalAvailableRam * 1024)
        '''containers = max(3, min (2*cores,min (1.8*DISKS,(Total available RAM) / MIN_CONTAINER_SIZE))))'''
        cluster["containers"] = round(max(3,
                                          min(2 * cluster["cpu"],
                                              min(ceil(1.8 * cluster["disk"]),
                                                  cluster["totalAvailableRam"] / cluster["minContainerSize"]))))

        '''ramPerContainers = max(2GB, RAM - reservedRam - hBaseRam) / containers'''
        cluster["ramPerContainer"] = abs(cluster["totalAvailableRam"] / cluster["containers"])
        '''If greater than 1GB, value will be in multiples of 512.'''
        if cluster["ramPerContainer"] > 1024:
            cluster["ramPerContainer"] = int(cluster["ramPerContainer"] / 512) * 512

        cluster["mapMemory"] = int(cluster["ramPerContainer"])
        cluster["reduceMemory"] = cluster["ramPerContainer"]
        cluster["amMemory"] = max(cluster["mapMemory"], cluster["reduceMemory"])

        return cluster

    def getConfigurationsValidationItems(self, services, hosts):
        """Returns array of Validation objects about issues with configuration values provided in services"""
        items = []

        recommendations = self.recommendConfigurations(services, hosts)
        recommendedDefaults = recommendations["recommendations"]["blueprint"]["configurations"]

        configurations = services["configurations"]
        for service in services["services"]:
            serviceName = service["StackServices"]["service_name"]
            validator = self.validateServiceConfigurations(serviceName)
            if validator is not None:
                for siteName, method in validator.items():
                    if siteName in recommendedDefaults:
                        siteProperties = getSiteProperties(configurations, siteName)
                        if siteProperties is not None:
                            resultItems = method(
                                siteProperties, recommendedDefaults[siteName]["properties"], configurations, services, hosts)
                            items.extend(resultItems)
        return items

    def getServiceConfigurationValidators(self):
        return {
            "GREENPLUM": {"greenplum-env": self.validateGPConfigurationsEnv},
            "HDFS": {"hadoop-env": self.validateHDFSConfigurationsEnv},
            "MAPREDUCE2": {"mapred-site": self.validateMapReduce2Configurations},
            "YARN": {"yarn-site": self.validateYARNConfigurations},
            "HBASE": {"hbase-env": self.validateHbaseEnvConfigurations},
            "AMBARI_METRICS": {"ams-hbase-site": self.validateAmsHbaseSiteConfigurations,
                               "ams-hbase-env": self.validateAmsHbaseEnvConfigurations,
                               "ams-site": self.validateAmsSiteConfigurations},
        }

    def validateGPConfigurationsEnv(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = []
        master_port_ambari_collision = None

        if properties['master_port'] == '5432' and component_on_ambari(services, 'GREENPLUM_MASTER'):
            master_port_ambari_collision = self.getErrorItem(
                'Master port will collide with Ambari database!  Please change port from 5432.')

        validationItems.append({'config-name': 'master_port', 'item': master_port_ambari_collision})

        return self.toConfigurationValidationProblems(validationItems, 'greenplum-env')

    def validateAmsSiteConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = []

        op_mode = properties.get("timeline.metrics.service.operation.mode")
        correct_op_mode_item = None
        if op_mode not in ("embedded", "distributed"):
            correct_op_mode_item = self.getErrorItem("Correct value should be set.")
            pass

        validationItems.extend(
            [{"config-name": 'timeline.metrics.service.operation.mode', "item": correct_op_mode_item}])
        return self.toConfigurationValidationProblems(validationItems, "ams-site")

    def validateAmsHbaseSiteConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):

        amsCollectorHosts = self.getComponentHostNames(services, "AMBARI_METRICS", "METRICS_COLLECTOR")
        ams_site = getSiteProperties(configurations, "ams-site")

        recommendedDiskSpace = 10485760
        # TODO validate configuration for multiple AMBARI_METRICS collectors
        if len(amsCollectorHosts) > 1:
            pass
        else:
            totalHostsCount = len(hosts["items"])
            if totalHostsCount > 400:
                recommendedDiskSpace = 104857600  # * 1k == 100 Gb
            elif totalHostsCount > 100:
                recommendedDiskSpace = 52428800  # * 1k == 50 Gb
            elif totalHostsCount > 50:
                recommendedDiskSpace = 20971520  # * 1k == 20 Gb

        validationItems = []
        for collectorHostName in amsCollectorHosts:
            for host in hosts["items"]:
                if host["Hosts"]["host_name"] == collectorHostName:
                    validationItems.extend(
                        [{"config-name": 'hbase.rootdir', "item": self.validatorEnoughDiskSpace(properties, 'hbase.rootdir', host["Hosts"], recommendedDiskSpace)}])
                    break

        rootdir_item = None
        op_mode = ams_site.get("timeline.metrics.service.operation.mode")
        hbase_rootdir = properties.get("hbase.rootdir")
        if op_mode == "distributed" and not hbase_rootdir.startswith("hdfs://"):
            rootdir_item = self.getWarnItem(
                "In distributed mode hbase.rootdir should point to HDFS. Collector will operate in embedded mode otherwise.")
            pass

        distributed_item = None
        distributed = properties.get("hbase.cluster.distributed")
        if hbase_rootdir.startswith("hdfs://") and not distributed.lower() == "true":
            distributed_item = self.getErrorItem(
                "Distributed property should be set to true if hbase.rootdir points to HDFS.")

        validationItems.extend([{"config-name": 'hbase.rootdir', "item": rootdir_item},
                                {"config-name": 'hbase.cluster.distributed', "item": distributed_item}])

        return self.toConfigurationValidationProblems(validationItems, "ams-hbase-site")

    def validateAmsHbaseEnvConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        regionServerItem = self.validatorLessThenDefaultValue(
            properties, recommendedDefaults, "hbase_regionserver_heapsize")
        masterItem = self.validatorLessThenDefaultValue(properties, recommendedDefaults, "hbase_master_heapsize")
        ams_env = getSiteProperties(configurations, "ams-env")
        logDirItem = self.validatorEqualsPropertyItem(properties, "hbase_log_dir",
                                                      ams_env, "metrics_collector_log_dir")
        masterHostItem = None

        if masterItem is None:
            hostComponents = {}
            hostMasterComponents = {}

            for service in services["services"]:
                for component in service["components"]:
                    if component["StackServiceComponents"]["hostnames"] is not None:
                        for hostName in component["StackServiceComponents"]["hostnames"]:
                            if hostName not in hostComponents.keys():
                                hostComponents[hostName] = []
                            hostComponents[hostName].append(component["StackServiceComponents"]["component_name"])
                            if self.isMasterComponent(component):
                                if hostName not in hostMasterComponents.keys():
                                    hostMasterComponents[hostName] = []
                                hostMasterComponents[hostName].append(
                                    component["StackServiceComponents"]["component_name"])

            amsCollectorHosts = self.getComponentHostNames(services, "AMBARI_METRICS", "METRICS_COLLECTOR")
            for collectorHostName in amsCollectorHosts:
                for host in hosts["items"]:
                    if host["Hosts"]["host_name"] == collectorHostName:
                        # AMS Collector co-hosted with other master components in bigger clusters
                        if len(hosts['items']) > 31 and \
                                len(hostMasterComponents[collectorHostName]) > 2 and \
                                host["Hosts"]["total_mem"] < 32 * 1024 * 1024:  # <32 Gb(total_mem in k)
                            masterHostMessage = "Host {0} is used by multiple master components ({1}). " \
                                                "It is recommended to use a separate host for the " \
                                                "Ambari Metrics Collector component and ensure " \
                                                "the host has sufficient memory available."

                            masterHostItem = self.getWarnItem(
                                masterHostMessage.format(
                                    collectorHostName, str(", ".join(hostMasterComponents[collectorHostName]))))

                        # No enough physical memory
                        # TODO Add AMBARI_METRICS Collector Xmx property to ams-env
                        requiredMemory = getMemorySizeRequired(hostComponents[collectorHostName], configurations)
                        if host["Hosts"]["total_mem"] * 1024 < requiredMemory:  # in bytes
                            message = "No enough total RAM on the host {0}, " \
                                      "at least {1} MB required for the components({2})" \
                                .format(collectorHostName, requiredMemory / 1048576,
                                        str(", ".join(hostComponents[collectorHostName])))  # MB
                            regionServerItem = self.getErrorItem(message)
                            masterItem = self.getErrorItem(message)
                            break

        validationItems = [{"config-name": "hbase_regionserver_heapsize", "item": regionServerItem},
                           {"config-name": "hbase_master_heapsize", "item": masterItem},
                           {"config-name": "hbase_master_heapsize", "item": masterHostItem},
                           {"config-name": "hbase_log_dir", "item": logDirItem}]
        return self.toConfigurationValidationProblems(validationItems, "ams-hbase-env")

    def validateServiceConfigurations(self, serviceName):
        return self.getServiceConfigurationValidators().get(serviceName, None)

    def toConfigurationValidationProblems(self, validationProblems, siteName):
        result = []
        for validationProblem in validationProblems:
            validationItem = validationProblem.get("item", None)
            if validationItem is not None:
                problem = {"type": 'configuration', "level": validationItem["level"], "message": validationItem["message"],
                           "config-type": siteName, "config-name": validationProblem["config-name"]}
                result.append(problem)
        return result

    def getWarnItem(self, message):
        return {"level": "WARN", "message": message}

    def getErrorItem(self, message):
        return {"level": "ERROR", "message": message}

    def validatorEnoughDiskSpace(self, properties, propertyName, hostInfo, reqiuredDiskSpace):
        if not propertyName in properties:
            return self.getErrorItem("Value should be set")
        dir = properties[propertyName]
        if dir.startswith("hdfs://"):
            return None  # TODO following code fails for hdfs://, is this valid check for hdfs?

        dir = re.sub("^file://", "", dir, count=1)
        mountPoints = {}
        for mountPoint in hostInfo["disk_info"]:
            mountPoints[mountPoint["mountpoint"]] = to_number(mountPoint["available"])
        mountPoint = getMountPointForDir(dir, mountPoints.keys())

        if not mountPoints:
            return self.getErrorItem("No disk info found on host {0}", hostInfo["host_name"])

        if mountPoints[mountPoint] < reqiuredDiskSpace:
            msg = "Ambari Metrics disk space requirements not met. \n" \
                  "Recommended disk space for partition {0} is {1}G"
            return self.getWarnItem(msg.format(mountPoint, reqiuredDiskSpace / 1048576))  # in Gb
        return None

    def validatorLessThenDefaultValue(self, properties, recommendedDefaults, propertyName):
        if not propertyName in properties:
            return self.getErrorItem("Value should be set")
        value = to_number(properties[propertyName])
        if value is None:
            return self.getErrorItem("Value should be integer")
        defaultValue = to_number(recommendedDefaults[propertyName])
        if defaultValue is None:
            return None
        if value < defaultValue:
            return self.getWarnItem("Value is less than the recommended default of {0}".format(defaultValue))
        return None

    def validatorEqualsPropertyItem(self, properties1, propertyName1,
                                    properties2, propertyName2,
                                    emptyAllowed=False):
        if not propertyName1 in properties1:
            return self.getErrorItem("Value should be set for %s" % propertyName1)
        if not propertyName2 in properties2:
            return self.getErrorItem("Value should be set for %s" % propertyName2)
        value1 = properties1.get(propertyName1)
        if value1 is None and not emptyAllowed:
            return self.getErrorItem("Empty value for %s" % propertyName1)
        value2 = properties2.get(propertyName2)
        if value2 is None and not emptyAllowed:
            return self.getErrorItem("Empty value for %s" % propertyName2)
        if value1 != value2:
            return self.getWarnItem("It is recommended to set equal values "
                                    "for properties {0} and {1}".format(propertyName1, propertyName2))

        return None

    def validateXmxValue(self, properties, recommendedDefaults, propertyName):
        if not propertyName in properties:
            return self.getErrorItem("Value should be set")
        value = properties[propertyName]
        defaultValue = recommendedDefaults[propertyName]
        if defaultValue is None:
            return self.getErrorItem("Config's default value can't be null or undefined")
        if not checkXmxValueFormat(value):
            return self.getErrorItem('Invalid value format')
        valueInt = formatXmxSizeToBytes(getXmxSize(value))
        defaultValueXmx = getXmxSize(defaultValue)
        defaultValueInt = formatXmxSizeToBytes(defaultValueXmx)
        if valueInt < defaultValueInt:
            return self.getWarnItem("Value is less than the recommended default of -Xmx" + defaultValueXmx)
        return None

    def validateMapReduce2Configurations(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = [{"config-name": 'mapreduce.map.java.opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'mapreduce.map.java.opts')},
                           {"config-name": 'mapreduce.reduce.java.opts', "item":
                            self.validateXmxValue(properties, recommendedDefaults, 'mapreduce.reduce.java.opts')},
                           {"config-name": 'mapreduce.task.io.sort.mb', "item":
                            self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.task.io.sort.mb')},
                           {"config-name": 'mapreduce.map.memory.mb', "item":
                            self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.map.memory.mb')},
                           {"config-name": 'mapreduce.reduce.memory.mb', "item":
                            self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.reduce.memory.mb')},
                           {"config-name": 'yarn.app.mapreduce.am.resource.mb', "item":
                            self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.app.mapreduce.am.resource.mb')},
                           {"config-name": 'yarn.app.mapreduce.am.command-opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'yarn.app.mapreduce.am.command-opts')}]
        return self.toConfigurationValidationProblems(validationItems, "mapred-site")

    def validateYARNConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = [{"config-name": 'yarn.nodemanager.resource.memory-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.nodemanager.resource.memory-mb')},
                           {"config-name": 'yarn.scheduler.minimum-allocation-mb', "item":
                            self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.scheduler.minimum-allocation-mb')},
                           {"config-name": 'yarn.scheduler.maximum-allocation-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.scheduler.maximum-allocation-mb')}]
        return self.toConfigurationValidationProblems(validationItems, "yarn-site")

    def validateHbaseEnvConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = [{"config-name": 'hbase_regionserver_heapsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'hbase_regionserver_heapsize')},
                           {"config-name": 'hbase_master_heapsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'hbase_master_heapsize')}]
        return self.toConfigurationValidationProblems(validationItems, "hbase-env")

    def validateHDFSConfigurationsEnv(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = [{"config-name": 'namenode_heapsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'namenode_heapsize')},
                           {"config-name": 'namenode_opt_newsize', "item":
                            self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'namenode_opt_newsize')},
                           {"config-name": 'namenode_opt_maxnewsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'namenode_opt_maxnewsize')}]
        return self.toConfigurationValidationProblems(validationItems, "hadoop-env")

    def getMastersWithMultipleInstances(self):
        return ['ZOOKEEPER_SERVER', 'HBASE_MASTER']

    def getNotValuableComponents(self):
        return ['JOURNALNODE', 'ZKFC', 'GANGLIA_MONITOR']

    def getNotPreferableOnServerComponents(self):
        return ['GANGLIA_SERVER']

    def getCardinalitiesDict(self):
        return {
            'ZOOKEEPER_SERVER': {"min": 3},
            'HBASE_MASTER': {"min": 1},
        }

    def getComponentLayoutSchemes(self):
        return {
            'NAMENODE': {"else": 0},
            'SECONDARY_NAMENODE': {"else": 1},
            'HBASE_MASTER': {6: 0, 31: 2, "else": 3},

            'HISTORYSERVER': {31: 1, "else": 2},
            'RESOURCEMANAGER': {31: 1, "else": 2},

            'OOZIE_SERVER': {6: 1, 31: 2, "else": 3},

            'HIVE_SERVER': {6: 1, 31: 2, "else": 4},
            'HIVE_METASTORE': {6: 1, 31: 2, "else": 4},
            'WEBHCAT_SERVER': {6: 1, 31: 2, "else": 4},
            'METRICS_COLLECTOR': {"else": 2},
        }

    def get_system_min_uid(self):
        login_defs = '/etc/login.defs'
        uid_min_tag = 'UID_MIN'
        comment_tag = '#'
        uid_min = uid_default = '1000'
        uid = None

        if os.path.exists(login_defs):
            with open(login_defs, 'r') as f:
                data = f.read().split('\n')
                # look for uid_min_tag in file
                uid = filter(lambda x: uid_min_tag in x, data)
                # filter all lines, where uid_min_tag was found in comments
                uid = filter(lambda x: x.find(comment_tag) > x.find(uid_min_tag) or x.find(comment_tag) == -1, uid)

            if uid is not None and len(uid) > 0:
                uid = uid[0]
                comment = uid.find(comment_tag)
                tag = uid.find(uid_min_tag)
                if comment == -1:
                    uid_tag = tag + len(uid_min_tag)
                    uid_min = uid[uid_tag:].strip()
                elif comment > tag:
                    uid_tag = tag + len(uid_min_tag)
                    uid_min = uid[uid_tag:comment].strip()

        # check result for value
        try:
            int(uid_min)
        except ValueError:
            return uid_default

  def getComponentLayoutValidations(self, services, hosts):
    """Returns array of Validation objects about issues with hostnames components assigned to"""
    items = []

    # Validating NAMENODE and SECONDARY_NAMENODE are on different hosts if possible
    hostsList = [host["Hosts"]["host_name"] for host in hosts["items"]]
    hostsCount = len(hostsList)

    componentsListList = [service["components"] for service in services["services"]]
    componentsList = [item for sublist in componentsListList for item in sublist]
    nameNodeHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "NAMENODE"]
    secondaryNameNodeHosts = [component["StackServiceComponents"]["hostnames"] for component in componentsList if component["StackServiceComponents"]["component_name"] == "SECONDARY_NAMENODE"]

    # Validating cardinality
    for component in componentsList:
      if component["StackServiceComponents"]["cardinality"] is not None:
         componentName = component["StackServiceComponents"]["component_name"]
         componentDisplayName = component["StackServiceComponents"]["display_name"]
         componentHostsCount = 0
         if component["StackServiceComponents"]["hostnames"] is not None:
           componentHostsCount = len(component["StackServiceComponents"]["hostnames"])
         cardinality = str(component["StackServiceComponents"]["cardinality"])
         # cardinality types: null, 1+, 1-2, 1, ALL
         message = None
         if "+" in cardinality:
           hostsMin = int(cardinality[:-1])
           if componentHostsCount < hostsMin:
             message = "At least {0} {1} components should be installed in cluster.".format(hostsMin, componentDisplayName)
         elif "-" in cardinality:
           nums = cardinality.split("-")
           hostsMin = int(nums[0])
           hostsMax = int(nums[1])
           if componentHostsCount > hostsMax or componentHostsCount < hostsMin:
             message = "Between {0} and {1} {2} components should be installed in cluster.".format(hostsMin, hostsMax, componentDisplayName)
         elif "ALL" == cardinality:
           if componentHostsCount != hostsCount:
             message = "{0} component should be installed on all hosts in cluster.".format(componentDisplayName)
         else:
           if componentHostsCount != int(cardinality):
             message = "Exactly {0} {1} components should be installed in cluster.".format(int(cardinality), componentDisplayName)

         if message is not None:
           items.append({"type": 'host-component', "level": 'ERROR', "message": message, "component-name": componentName})

    # Validating host-usage
    usedHostsListList = [component["StackServiceComponents"]["hostnames"] for component in componentsList if not self.isComponentNotValuable(component)]
    usedHostsList = [item for sublist in usedHostsListList for item in sublist]
    nonUsedHostsList = [item for item in hostsList if item not in usedHostsList]
    for host in nonUsedHostsList:
      items.append( { "type": 'host-component', "level": 'ERROR', "message": 'Host is not used', "host": str(host) } )

    return items

  def getServiceConfigurationRecommenderDict(self):
    return {
      "YARN": self.recommendYARNConfigurations,
      "MAPREDUCE2": self.recommendMapReduce2Configurations,
      "HDFS": self.recommendHDFSConfigurations,
      "HBASE": self.recommendHbaseEnvConfigurations,
      "AMBARI_METRICS": self.recommendAmsConfigurations
    }

  def putProperty(self, config, configType):
    if configType not in config or "properties" not in config[configType]:
      config[configType] = {"properties": {}}
    def appendProperty(key, value):
      config[configType]["properties"][key] = str(value)
    return appendProperty

  def recommendYARNConfigurations(self, configurations, clusterData, services, hosts):
    putYarnProperty = self.putProperty(configurations, "yarn-site")
    putYarnEnvProperty = self.putProperty(configurations, "yarn-env")
    putYarnProperty('yarn.nodemanager.resource.memory-mb', int(round(clusterData['containers'] * clusterData['ramPerContainer'])))
    putYarnProperty('yarn.scheduler.minimum-allocation-mb', int(clusterData['ramPerContainer']))
    putYarnProperty('yarn.scheduler.maximum-allocation-mb', int(round(clusterData['containers'] * clusterData['ramPerContainer'])))
    putYarnEnvProperty('min_user_id', self.get_system_min_uid())

  def recommendMapReduce2Configurations(self, configurations, clusterData, services, hosts):
    putMapredProperty = self.putProperty(configurations, "mapred-site")
    putMapredProperty('yarn.app.mapreduce.am.resource.mb', int(clusterData['amMemory']))
    putMapredProperty('yarn.app.mapreduce.am.command-opts', "-Xmx" + str(int(round(0.8 * clusterData['amMemory']))) + "m")
    putMapredProperty('mapreduce.map.memory.mb', clusterData['mapMemory'])
    putMapredProperty('mapreduce.reduce.memory.mb', int(clusterData['reduceMemory']))
    putMapredProperty('mapreduce.map.java.opts', "-Xmx" + str(int(round(0.8 * clusterData['mapMemory']))) + "m")
    putMapredProperty('mapreduce.reduce.java.opts', "-Xmx" + str(int(round(0.8 * clusterData['reduceMemory']))) + "m")
    putMapredProperty('mapreduce.task.io.sort.mb', min(int(round(0.4 * clusterData['mapMemory'])), 1024))
 
  def recommendHDFSConfigurations(self, configurations, clusterData, services, hosts):
    putHDFSProperty = self.putProperty(configurations, "hadoop-env")
    putHDFSProperty('namenode_heapsize', max(int(clusterData['totalAvailableRam'] / 2), 1024))
    putHDFSProperty = self.putProperty(configurations, "hadoop-env")
    putHDFSProperty('namenode_opt_newsize', max(int(clusterData['totalAvailableRam'] / 8), 128))
    putHDFSProperty = self.putProperty(configurations, "hadoop-env")
    putHDFSProperty('namenode_opt_maxnewsize', max(int(clusterData['totalAvailableRam'] / 8), 256))

  def recommendHbaseEnvConfigurations(self, configurations, clusterData, services, hosts):
    putHbaseProperty = self.putProperty(configurations, "hbase-env")
    putHbaseProperty('hbase_regionserver_heapsize', int(clusterData['hbaseRam']) * 1024)
    putHbaseProperty('hbase_master_heapsize', int(clusterData['hbaseRam']) * 1024)

  def recommendAmsConfigurations(self, configurations, clusterData, services, hosts):
    putAmsEnvProperty = self.putProperty(configurations, "ams-env")
    putAmsEnvProperty = self.putProperty(configurations, "ams-env")
    putAmsHbaseSiteProperty = self.putProperty(configurations, "ams-hbase-site")
    putTimelineServiceProperty = self.putProperty(configurations, "ams-site")
    putHbaseEnvProperty = self.putProperty(configurations, "ams-hbase-env")

    amsCollectorHosts = self.getComponentHostNames(services, "AMBARI_METRICS", "METRICS_COLLECTOR")
    putHbaseEnvProperty("hbase_regionserver_heapsize", "1024m")
    # blockCache = 0.3, memstore = 0.35, phoenix-server = 0.15, phoenix-client = 0.25
    putAmsHbaseSiteProperty("hfile.block.cache.size", 0.3)
    putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.upperLimit", 0.35)
    putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.lowerLimit", 0.3)
    putTimelineServiceProperty("timeline.metrics.host.aggregator.ttl", 86400)

    # TODO recommend configuration for multiple AMBARI_METRICS collectors
    if len(amsCollectorHosts) > 1:
      pass
    else:
      totalHostsCount = len(hosts["items"])
      # blockCache = 0.3, memstore = 0.3, phoenix-server = 0.2, phoenix-client = 0.3
      if totalHostsCount >= 400:
        putHbaseEnvProperty("hbase_master_heapsize", "12288m")
        putAmsEnvProperty("metrics_collector_heapsize", "8192m")
        putAmsHbaseSiteProperty("hbase.regionserver.handler.count", 60)
        putAmsHbaseSiteProperty("hbase.regionserver.hlog.blocksize", 134217728)
        putAmsHbaseSiteProperty("hbase.regionserver.maxlogs", 64)
        putAmsHbaseSiteProperty("hbase.hregion.memstore.flush.size", 268435456)
        putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.upperLimit", 0.3)
        putAmsHbaseSiteProperty("hbase.regionserver.global.memstore.lowerLimit", 0.25)
        putAmsHbaseSiteProperty("phoenix.query.maxGlobalMemoryPercentage", 20)
        putTimelineServiceProperty("phoenix.query.maxGlobalMemoryPercentage", 30)
        putHbaseEnvProperty("hbase_master_xmn_size", "512m")
      elif totalHostsCount >= 100:
        putHbaseEnvProperty("hbase_master_heapsize", "6144m")
        putAmsEnvProperty("metrics_collector_heapsize", "4096m")
        putAmsHbaseSiteProperty("hbase.regionserver.handler.count", 60)
        putAmsHbaseSiteProperty("hbase.regionserver.hlog.blocksize", 134217728)
        putAmsHbaseSiteProperty("hbase.regionserver.maxlogs", 64)
        putAmsHbaseSiteProperty("hbase.hregion.memstore.flush.size", 268435456)
        putHbaseEnvProperty("hbase_master_xmn_size", "512m")
      elif totalHostsCount >= 50:
        putHbaseEnvProperty("hbase_master_heapsize", "2048m")
        putAmsEnvProperty("metrics_collector_heapsize", "2048m")
        putHbaseEnvProperty("hbase_master_xmn_size", "256m")
      else:
        putHbaseEnvProperty("hbase_master_heapsize", "1024m")
        putAmsEnvProperty("metrics_collector_heapsize", "512m")
        putHbaseEnvProperty("hbase_master_xmn_size", "128m")

  def getConfigurationClusterSummary(self, servicesList, hosts, components):

    hBaseInstalled = False
    if 'HBASE' in servicesList:
      hBaseInstalled = True

    cluster = {
      "cpu": 0,
      "disk": 0,
      "ram": 0,
      "hBaseInstalled": hBaseInstalled,
      "components": components
    }

    if len(hosts["items"]) > 0:
      host = hosts["items"][0]["Hosts"]
      cluster["cpu"] = host["cpu_count"]
      cluster["disk"] = len(host["disk_info"])
      cluster["ram"] = int(host["total_mem"] / (1024 * 1024))

    ramRecommendations = [
      {"os":1, "hbase":1},
      {"os":2, "hbase":1},
      {"os":2, "hbase":2},
      {"os":4, "hbase":4},
      {"os":6, "hbase":8},
      {"os":8, "hbase":8},
      {"os":8, "hbase":8},
      {"os":12, "hbase":16},
      {"os":24, "hbase":24},
      {"os":32, "hbase":32},
      {"os":64, "hbase":64}
    ]
    index = {
      cluster["ram"] <= 4: 0,
      4 < cluster["ram"] <= 8: 1,
      8 < cluster["ram"] <= 16: 2,
      16 < cluster["ram"] <= 24: 3,
      24 < cluster["ram"] <= 48: 4,
      48 < cluster["ram"] <= 64: 5,
      64 < cluster["ram"] <= 72: 6,
      72 < cluster["ram"] <= 96: 7,
      96 < cluster["ram"] <= 128: 8,
      128 < cluster["ram"] <= 256: 9,
      256 < cluster["ram"]: 10
    }[1]
    cluster["reservedRam"] = ramRecommendations[index]["os"]
    cluster["hbaseRam"] = ramRecommendations[index]["hbase"]

    cluster["minContainerSize"] = {
      cluster["ram"] <= 4: 256,
      4 < cluster["ram"] <= 8: 512,
      8 < cluster["ram"] <= 24: 1024,
      24 < cluster["ram"]: 2048
    }[1]

    totalAvailableRam = cluster["ram"] - cluster["reservedRam"]
    if cluster["hBaseInstalled"]:
      totalAvailableRam -= cluster["hbaseRam"]
    cluster["totalAvailableRam"] = max(2048, totalAvailableRam * 1024)
    '''containers = max(3, min (2*cores,min (1.8*DISKS,(Total available RAM) / MIN_CONTAINER_SIZE))))'''
    cluster["containers"] = round(max(3,
                                min(2 * cluster["cpu"],
                                    min(ceil(1.8 * cluster["disk"]),
                                            cluster["totalAvailableRam"] / cluster["minContainerSize"]))))

    '''ramPerContainers = max(2GB, RAM - reservedRam - hBaseRam) / containers'''
    cluster["ramPerContainer"] = abs(cluster["totalAvailableRam"] / cluster["containers"])
    '''If greater than 1GB, value will be in multiples of 512.'''
    if cluster["ramPerContainer"] > 1024:
      cluster["ramPerContainer"] = int(cluster["ramPerContainer"] / 512) * 512

    cluster["mapMemory"] = int(cluster["ramPerContainer"])
    cluster["reduceMemory"] = cluster["ramPerContainer"]
    cluster["amMemory"] = max(cluster["mapMemory"], cluster["reduceMemory"])

    return cluster

  def getConfigurationsValidationItems(self, services, hosts):
    """Returns array of Validation objects about issues with configuration values provided in services"""
    items = []

    recommendations = self.recommendConfigurations(services, hosts)
    recommendedDefaults = recommendations["recommendations"]["blueprint"]["configurations"]

    configurations = services["configurations"]
    for service in services["services"]:
      serviceName = service["StackServices"]["service_name"]
      validator = self.validateServiceConfigurations(serviceName)
      if validator is not  None:
        for siteName, method in validator.items():
          if siteName in recommendedDefaults:
            siteProperties = getSiteProperties(configurations, siteName)
            if siteProperties is not None:
              resultItems = method(siteProperties, recommendedDefaults[siteName]["properties"], configurations, services, hosts)
              items.extend(resultItems)
    return items

  def getServiceConfigurationValidators(self):
    return {
      "HDFS": {"hadoop-env": self.validateHDFSConfigurationsEnv},
      "MAPREDUCE2": {"mapred-site": self.validateMapReduce2Configurations},
      "YARN": {"yarn-site": self.validateYARNConfigurations},
      "HBASE": {"hbase-env": self.validateHbaseEnvConfigurations},
      "AMBARI_METRICS": {"ams-hbase-site": self.validateAmsHbaseSiteConfigurations,
              "ams-hbase-env": self.validateAmsHbaseEnvConfigurations,
              "ams-site": self.validateAmsSiteConfigurations},
      "GREENPLUM": {'greenplum-env': self.validateGreenplumConfigurationsEnv},
    }

  def validateAmsSiteConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
    validationItems = []

    op_mode = properties.get("timeline.metrics.service.operation.mode")
    correct_op_mode_item = None
    if op_mode not in ("embedded", "distributed"):
      correct_op_mode_item = self.getErrorItem("Correct value should be set.")
      pass

    validationItems.extend([{"config-name":'timeline.metrics.service.operation.mode', "item": correct_op_mode_item }])
    return self.toConfigurationValidationProblems(validationItems, "ams-site")

  def validateAmsHbaseSiteConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):

    amsCollectorHosts = self.getComponentHostNames(services, "AMBARI_METRICS", "METRICS_COLLECTOR")
    ams_site = getSiteProperties(configurations, "ams-site")

    recommendedDiskSpace = 10485760
    # TODO validate configuration for multiple AMBARI_METRICS collectors
    if len(amsCollectorHosts) > 1:
      pass
    else:
      totalHostsCount = len(hosts["items"])
      if totalHostsCount > 400:
        recommendedDiskSpace  = 104857600  # * 1k == 100 Gb
      elif totalHostsCount > 100:
        recommendedDiskSpace  = 52428800  # * 1k == 50 Gb
      elif totalHostsCount > 50:
        recommendedDiskSpace  = 20971520  # * 1k == 20 Gb


    validationItems = []
    for collectorHostName in amsCollectorHosts:
      for host in hosts["items"]:
        if host["Hosts"]["host_name"] == collectorHostName:
          validationItems.extend([ {"config-name": 'hbase.rootdir', "item": self.validatorEnoughDiskSpace(properties, 'hbase.rootdir', host["Hosts"], recommendedDiskSpace)}])
          break

    rootdir_item = None
    op_mode = ams_site.get("timeline.metrics.service.operation.mode")
    hbase_rootdir = properties.get("hbase.rootdir")
    if op_mode == "distributed" and not hbase_rootdir.startswith("hdfs://"):
      rootdir_item = self.getWarnItem("In distributed mode hbase.rootdir should point to HDFS. Collector will operate in embedded mode otherwise.")
      pass

    distributed_item = None
    distributed = properties.get("hbase.cluster.distributed")
    if hbase_rootdir.startswith("hdfs://") and not distributed.lower() == "true":
      distributed_item = self.getErrorItem("Distributed property should be set to true if hbase.rootdir points to HDFS.")

    validationItems.extend([{"config-name":'hbase.rootdir', "item": rootdir_item },
                            {"config-name":'hbase.cluster.distributed', "item": distributed_item }])

    return self.toConfigurationValidationProblems(validationItems, "ams-hbase-site")

  def validateAmsHbaseEnvConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
    regionServerItem = self.validatorLessThenDefaultValue(properties, recommendedDefaults, "hbase_regionserver_heapsize")
    masterItem = self.validatorLessThenDefaultValue(properties, recommendedDefaults, "hbase_master_heapsize")
    ams_env = getSiteProperties(configurations, "ams-env")
    logDirItem = self.validatorEqualsPropertyItem(properties, "hbase_log_dir",
                                                  ams_env, "metrics_collector_log_dir")
    masterHostItem = None

    if masterItem is None:
      hostComponents = {}
      hostMasterComponents = {}

      for service in services["services"]:
        for component in service["components"]:
          if component["StackServiceComponents"]["hostnames"] is not None:
            for hostName in component["StackServiceComponents"]["hostnames"]:
              if hostName not in hostComponents.keys():
                hostComponents[hostName] = []
              hostComponents[hostName].append(component["StackServiceComponents"]["component_name"])
              if self.isMasterComponent(component):
                if hostName not in hostMasterComponents.keys():
                  hostMasterComponents[hostName] = []
                hostMasterComponents[hostName].append(component["StackServiceComponents"]["component_name"])

      amsCollectorHosts = self.getComponentHostNames(services, "AMBARI_METRICS", "METRICS_COLLECTOR")
      for collectorHostName in amsCollectorHosts:
        for host in hosts["items"]:
          if host["Hosts"]["host_name"] == collectorHostName:
            # AMS Collector co-hosted with other master components in bigger clusters
            if len(hosts['items']) > 31 and \
              len(hostMasterComponents[collectorHostName]) > 2 and \
              host["Hosts"]["total_mem"] < 32*1024*1024: # <32 Gb(total_mem in k)
              masterHostMessage = "Host {0} is used by multiple master components ({1}). " \
                                  "It is recommended to use a separate host for the " \
                                  "Ambari Metrics Collector component and ensure " \
                                  "the host has sufficient memory available."

              masterHostItem = self.getWarnItem(
                masterHostMessage.format(
                  collectorHostName, str(", ".join(hostMasterComponents[collectorHostName]))))

            # No enough physical memory
            # TODO Add AMBARI_METRICS Collector Xmx property to ams-env
            requiredMemory = getMemorySizeRequired(hostComponents[collectorHostName], configurations)
            if host["Hosts"]["total_mem"] * 1024 < requiredMemory:  # in bytes
              message = "No enough total RAM on the host {0}, " \
                        "at least {1} MB required for the components({2})" \
                .format(collectorHostName, requiredMemory/1048576,
                        str(", ".join(hostComponents[collectorHostName])))  # MB
              regionServerItem = self.getErrorItem(message)
              masterItem = self.getErrorItem(message)
              break

    validationItems = [{"config-name": "hbase_regionserver_heapsize", "item": regionServerItem},
                       {"config-name": "hbase_master_heapsize", "item": masterItem},
                       {"config-name": "hbase_master_heapsize", "item": masterHostItem},
                       {"config-name": "hbase_log_dir", "item": logDirItem}]
    return self.toConfigurationValidationProblems(validationItems, "ams-hbase-env")


  def validateServiceConfigurations(self, serviceName):
    return self.getServiceConfigurationValidators().get(serviceName, None)

  def validateGreenplumConfigurationsEnv(self, properties, recommendedDefaults, configurations, services, hosts):
    return self.toConfigurationValidationProblems([
      {'config-name': 'port_master', 'item': self.getErrorItem('Some error with master port') }
    ], 'greenplum-env')

  def toConfigurationValidationProblems(self, validationProblems, siteName):
    result = []
    for validationProblem in validationProblems:
      validationItem = validationProblem.get("item", None)
      if validationItem is not None:
        problem = {"type": 'configuration', "level": validationItem["level"], "message": validationItem["message"],
                   "config-type": siteName, "config-name": validationProblem["config-name"] }
        result.append(problem)
    return result

  def getWarnItem(self, message):
    return {"level": "WARN", "message": message}

  def getErrorItem(self, message):
    return {"level": "ERROR", "message": message}

  def validatorEnoughDiskSpace(self, properties, propertyName, hostInfo, reqiuredDiskSpace):
    if not propertyName in properties:
      return self.getErrorItem("Value should be set")
    dir = properties[propertyName]
    if dir.startswith("hdfs://"):
      return None #TODO following code fails for hdfs://, is this valid check for hdfs?

    dir = re.sub("^file://", "", dir, count=1)
    mountPoints = {}
    for mountPoint in hostInfo["disk_info"]:
      mountPoints[mountPoint["mountpoint"]] = to_number(mountPoint["available"])
    mountPoint = getMountPointForDir(dir, mountPoints.keys())

    if not mountPoints:
      return self.getErrorItem("No disk info found on host {0}", hostInfo["host_name"])

    if mountPoints[mountPoint] < reqiuredDiskSpace:
      msg = "Ambari Metrics disk space requirements not met. \n" \
            "Recommended disk space for partition {0} is {1}G"
      return self.getWarnItem(msg.format(mountPoint, reqiuredDiskSpace/1048576)) # in Gb
    return None

  def validatorLessThenDefaultValue(self, properties, recommendedDefaults, propertyName):
    if not propertyName in properties:
      return self.getErrorItem("Value should be set")
    value = to_number(properties[propertyName])
    if value is None:
      return self.getErrorItem("Value should be integer")
    defaultValue = to_number(recommendedDefaults[propertyName])
    if defaultValue is None:
      return None
    if value < defaultValue:
      return self.getWarnItem("Value is less than the recommended default of {0}".format(defaultValue))
    return None

  def validatorEqualsPropertyItem(self, properties1, propertyName1,
                                  properties2, propertyName2,
                                  emptyAllowed=False):
    if not propertyName1 in properties1:
      return self.getErrorItem("Value should be set for %s" % propertyName1)
    if not propertyName2 in properties2:
      return self.getErrorItem("Value should be set for %s" % propertyName2)
    value1 = properties1.get(propertyName1)
    if value1 is None and not emptyAllowed:
      return self.getErrorItem("Empty value for %s" % propertyName1)
    value2 = properties2.get(propertyName2)
    if value2 is None and not emptyAllowed:
      return self.getErrorItem("Empty value for %s" % propertyName2)
    if value1 != value2:
      return self.getWarnItem("It is recommended to set equal values "
             "for properties {0} and {1}".format(propertyName1, propertyName2))

    return None

  def validateXmxValue(self, properties, recommendedDefaults, propertyName):
    if not propertyName in properties:
      return self.getErrorItem("Value should be set")
    value = properties[propertyName]
    defaultValue = recommendedDefaults[propertyName]
    if defaultValue is None:
      return self.getErrorItem("Config's default value can't be null or undefined")
    if not checkXmxValueFormat(value):
      return self.getErrorItem('Invalid value format')
    valueInt = formatXmxSizeToBytes(getXmxSize(value))
    defaultValueXmx = getXmxSize(defaultValue)
    defaultValueInt = formatXmxSizeToBytes(defaultValueXmx)
    if valueInt < defaultValueInt:
      return self.getWarnItem("Value is less than the recommended default of -Xmx" + defaultValueXmx)
    return None

  def validateMapReduce2Configurations(self, properties, recommendedDefaults, configurations, services, hosts):
    validationItems = [ {"config-name": 'mapreduce.map.java.opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'mapreduce.map.java.opts')},
                        {"config-name": 'mapreduce.reduce.java.opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'mapreduce.reduce.java.opts')},
                        {"config-name": 'mapreduce.task.io.sort.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.task.io.sort.mb')},
                        {"config-name": 'mapreduce.map.memory.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.map.memory.mb')},
                        {"config-name": 'mapreduce.reduce.memory.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'mapreduce.reduce.memory.mb')},
                        {"config-name": 'yarn.app.mapreduce.am.resource.mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.app.mapreduce.am.resource.mb')},
                        {"config-name": 'yarn.app.mapreduce.am.command-opts', "item": self.validateXmxValue(properties, recommendedDefaults, 'yarn.app.mapreduce.am.command-opts')} ]
    return self.toConfigurationValidationProblems(validationItems, "mapred-site")

  def validateYARNConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
    validationItems = [ {"config-name": 'yarn.nodemanager.resource.memory-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.nodemanager.resource.memory-mb')},
                        {"config-name": 'yarn.scheduler.minimum-allocation-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.scheduler.minimum-allocation-mb')},
                        {"config-name": 'yarn.scheduler.maximum-allocation-mb', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'yarn.scheduler.maximum-allocation-mb')} ]
    return self.toConfigurationValidationProblems(validationItems, "yarn-site")

  def validateHbaseEnvConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
    validationItems = [ {"config-name": 'hbase_regionserver_heapsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'hbase_regionserver_heapsize')},
                        {"config-name": 'hbase_master_heapsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'hbase_master_heapsize')} ]
    return self.toConfigurationValidationProblems(validationItems, "hbase-env")

  def validateHDFSConfigurationsEnv(self, properties, recommendedDefaults, configurations, services, hosts):
    validationItems = [ {"config-name": 'namenode_heapsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'namenode_heapsize')},
                        {"config-name": 'namenode_opt_newsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'namenode_opt_newsize')},
                        {"config-name": 'namenode_opt_maxnewsize', "item": self.validatorLessThenDefaultValue(properties, recommendedDefaults, 'namenode_opt_maxnewsize')}]
    return self.toConfigurationValidationProblems(validationItems, "hadoop-env")

  def getMastersWithMultipleInstances(self):
    return ['ZOOKEEPER_SERVER', 'HBASE_MASTER']

  def getNotValuableComponents(self):
    return ['JOURNALNODE', 'ZKFC', 'GANGLIA_MONITOR']

  def getNotPreferableOnServerComponents(self):
    return ['GANGLIA_SERVER']

  def getCardinalitiesDict(self):
    return {
      'ZOOKEEPER_SERVER': {"min": 3},
      'HBASE_MASTER': {"min": 1},
      }

  def getComponentLayoutSchemes(self):
    return {
      'NAMENODE': {"else": 0},
      'SECONDARY_NAMENODE': {"else": 1},
      'HBASE_MASTER': {6: 0, 31: 2, "else": 3},

      'HISTORYSERVER': {31: 1, "else": 2},
      'RESOURCEMANAGER': {31: 1, "else": 2},

      'OOZIE_SERVER': {6: 1, 31: 2, "else": 3},

      'HIVE_SERVER': {6: 1, 31: 2, "else": 4},
      'HIVE_METASTORE': {6: 1, 31: 2, "else": 4},
      'WEBHCAT_SERVER': {6: 1, 31: 2, "else": 4},
      'METRICS_COLLECTOR': {"else": 2},
      }

  def get_system_min_uid(self):
    login_defs = '/etc/login.defs'
    uid_min_tag = 'UID_MIN'
    comment_tag = '#'
    uid_min = uid_default = '1000'
    uid = None

    if os.path.exists(login_defs):
      with open(login_defs, 'r') as f:
        data = f.read().split('\n')
        # look for uid_min_tag in file
        uid = filter(lambda x: uid_min_tag in x, data)
        # filter all lines, where uid_min_tag was found in comments
        uid = filter(lambda x: x.find(comment_tag) > x.find(uid_min_tag) or x.find(comment_tag) == -1, uid)

      if uid is not None and len(uid) > 0:
        uid = uid[0]
        comment = uid.find(comment_tag)
        tag = uid.find(uid_min_tag)
        if comment == -1:
          uid_tag = tag + len(uid_min_tag)
          uid_min = uid[uid_tag:].strip()
        elif comment > tag:
          uid_tag = tag + len(uid_min_tag)
          uid_min = uid[uid_tag:comment].strip()

    # check result for value
    try:
      int(uid_min)
    except ValueError:
      return uid_default

    return uid_min


# Validation helper methods
def getSiteProperties(configurations, siteName):
  siteConfig = configurations.get(siteName)
  if siteConfig is None:
    return None
  return siteConfig.get("properties")

def to_number(s):
  try:
    return int(re.sub("\D", "", s))
  except ValueError:
    return None

def checkXmxValueFormat(value):
  p = re.compile('-Xmx(\d+)(b|k|m|g|p|t|B|K|M|G|P|T)?')
  matches = p.findall(value)
  return len(matches) == 1

def getXmxSize(value):
  p = re.compile("-Xmx(\d+)(.?)")
  result = p.findall(value)[0]
  if len(result) > 1:
    # result[1] - is a space or size formatter (b|k|m|g etc)
    return result[0] + result[1].lower()
  return result[0]

def formatXmxSizeToBytes(value):
  value = value.lower()
  if len(value) == 0:
    return 0
  modifier = value[-1]

  if modifier == ' ' or modifier in "0123456789":
    modifier = 'b'
  m = {
    modifier == 'b': 1,
    modifier == 'k': 1024,
    modifier == 'm': 1024 * 1024,
    modifier == 'g': 1024 * 1024 * 1024,
    modifier == 't': 1024 * 1024 * 1024 * 1024,
    modifier == 'p': 1024 * 1024 * 1024 * 1024 * 1024
    }[1]
  return to_number(value) * m

def getPort(address):
  """
  Extracts port from the address like 0.0.0.0:1019
  """
  if address is None:
    return None
  m = re.search(r'(?:http(?:s)?://)?([\w\d.]*):(\d{1,5})', address)
  if m is not None:
    return int(m.group(2))
  else:
    return None

def isSecurePort(port):
  """
  Returns True if port is root-owned at *nix systems
  """
  if port is not None:
    return port < 1024
  else:
    return False

def getMountPointForDir(dir, mountPoints):
  """
  :param dir: Directory to check, even if it doesn't exist.
  :return: Returns the closest mount point as a string for the directory.
  if the "dir" variable is None, will return None.
  If the directory does not exist, will return "/".
  """
  bestMountFound = None
  if dir:
    dir = dir.strip().lower()

    # If the path is "/hadoop/hdfs/data", then possible matches for mounts could be
    # "/", "/hadoop/hdfs", and "/hadoop/hdfs/data".
    # So take the one with the greatest number of segments.
    for mountPoint in mountPoints:
      if dir.startswith(mountPoint):
        if bestMountFound is None:
          bestMountFound = mountPoint
        elif bestMountFound.count(os.path.sep) < mountPoint.count(os.path.sep):
          bestMountFound = mountPoint

  return bestMountFound

def getHeapsizeProperties():
  return { "NAMENODE": [{"config-name": "hadoop-env",
                         "property": "namenode_heapsize",
                         "default": "1024m"}],
           "DATANODE": [{"config-name": "hadoop-env",
                         "property": "dtnode_heapsize",
                         "default": "1024m"}],
           "REGIONSERVER": [{"config-name": "hbase-env",
                             "property": "hbase_regionserver_heapsize",
                             "default": "1024m"}],
           "HBASE_MASTER": [{"config-name": "hbase-env",
                             "property": "hbase_master_heapsize",
                             "default": "1024m"}],
           "HIVE_CLIENT": [{"config-name": "hive-site",
                            "property": "hive.heapsize",
                            "default": "1024m"}],
           "HISTORYSERVER": [{"config-name": "mapred-env",
                              "property": "jobhistory_heapsize",
                              "default": "1024m"}],
           "OOZIE_SERVER": [{"config-name": "oozie-env",
                             "property": "oozie_heapsize",
                             "default": "1024m"}],
           "RESOURCEMANAGER": [{"config-name": "yarn-env",
                                "property": "resourcemanager_heapsize",
                                "default": "1024m"}],
           "NODEMANAGER": [{"config-name": "yarn-env",
                            "property": "nodemanager_heapsize",
                            "default": "1024m"}],
           "APP_TIMELINE_SERVER": [{"config-name": "yarn-env",
                                    "property": "apptimelineserver_heapsize",
                                    "default": "1024m"}],
           "ZOOKEEPER_SERVER": [{"config-name": "zookeeper-env",
                                 "property": "zookeeper_heapsize",
                                 "default": "1024m"}],
           "METRICS_COLLECTOR": [{"config-name": "ams-hbase-env",
                                   "property": "hbase_master_heapsize",
                                   "default": "1024m"},
                                 {"config-name": "ams-env",
                                   "property": "metrics_collector_heapsize",
                                   "default": "512m"}],
           }

def getMemorySizeRequired(components, configurations):
  totalMemoryRequired = 512*1024*1024 # 512Mb for OS needs
  for component in components:
    if component in getHeapsizeProperties().keys():
      heapSizeProperties = getHeapsizeProperties()[component]
      for heapSizeProperty in heapSizeProperties:
        try:
          properties = configurations[heapSizeProperty["config-name"]]["properties"]
          heapsize = properties[heapSizeProperty["property"]]
        except KeyError:
          heapsize = heapSizeProperty["default"]

        # Assume Mb if no modifier
        if len(heapsize) > 1 and heapsize[-1] in '0123456789':
          heapsize = str(heapsize) + "m"

        totalMemoryRequired += formatXmxSizeToBytes(heapsize)

  return totalMemoryRequired
