#!/bin/bash

if [ "$EUID" != 0 ]; then
        echo "Please run as root user"
        exit 1
fi

function installDesiredPackages() {
    yum install -y vim screen || return 1
}

# Vagrant specific
function vagrantSetupHostsFile() {
    # Fixes issue #1
    sed -i "s;^127\.0\.0\.1\(.*\);127.0.0.1 localhost;" /etc/hosts || return 1
}

# Vagrant specific
function vagrantCreateSharedKeys () {
    if [ ! -d ~/.ssh ]; then
        mkdir ~/.ssh || return 1
    fi
    
    cat /vagrant/keys/private_key.pub >> ~/.ssh/authorized_keys || return 1
    cp /vagrant/keys/private_key ~/.ssh/id_rsa || return 1
    cp /vagrant/keys/private_key.pub ~/.ssh/id_rsa.pub || return 1
}

function setupApache2() {
    service httpd status &> /dev/null
    if [ $? -ne 0 ]; then
        yum install -y httpd || return 1
        service httpd start || return 1
        chkconfig httpd on || return 1
    fi
}

function setupNTPD() {
    yum install -y ntp ntpdate || return 1
    
    # Configure and sync up time. Make sure ntpd starts up on restart.
    service ntpd stop || return 1
    ntpdate pool.ntp.org || return 1
    service ntpd start || return 1
    chkconfig ntpd on || return 1
}

function disableFirewall() {
    # Turn off iptables and make sure it doesn't boot up on restart.
    service iptables stop || return  1
    chkconfig iptables off || return 1
}

function removeMemoryLimitationOnUsers() {
    # Remove memory limitation on users.
    sed -i '/\*.*.soft.*.nproc.*.1024.*$/d' /etc/security/limits.d/90-nproc.conf || return 1
}

function setSystemScheduling() {
    sed -i '/kernel/ s/$/ elevator=deadline/' /boot/grub/grub.conf || return 1
}

function disableTHP() {
    sed -i '/kernel/ s/$/ transparent_hugepage=never/' /boot/grub/grub.conf || return 1
    echo never > /sys/kernel/mm/transparent_hugepage/enabled || return 1
}

function disableSelinux() {
    # Turn off SELINUX permanently and temporarily.
    sed -i 's/^SELINUX=.*$/SELINUX=disabled/' /etc/selinux/config || return 1
    echo 0 > /selinux/enforce || return 1
}

function configureSSH() {
    # Configure sshd to enable RootLogin and PasswordAuthentication, then restart sshd.
    # NOTE - This may not be required if there is a common key on mdw that can ssh into other hosts before the Greenplum installer runs.
    sed -i -e 's/#PermitRootLogin.*$/PermitRootLogin yes/g' -e 's/PasswordAuthentication .*$/PasswordAuthentication yes/' /etc/ssh/sshd_config || return 1
    service sshd restart || return 1
}

function setupAmbariExtensions() {
    # Download Ambari zData Extensions and install it.
    cd ~
    currentUrl=https://s3-us-west-2.amazonaws.com/zdata-ambari/releases/zdata-ambari-stack-52c1dbb0.tar.gz
    curl $currentUrl -o zdata-ambari-stack.tar.gz || return 1
    tar -xzf zdata-ambari-stack*.tar.gz || return 1
    cd zdata-ambari-stack* && make install || return 1
    cd ~
}

function createCustomLocalRepo() {
    # Directory to contain custom local repo.
    localRepoDir=/var/www/html/ambari-extensions
    # Directory of artifacts that should be put into custom local repo (optional).
    vagrantRepoItemsDir=/vagrant/artifacts/repoItems
    
    setupApache2 || return 1

    yum install -y createrepo || return 1
    mkdir -p $localRepoDir || return 1 
    
    if [ -f "$vagrantRepoItemsDir" ]; then
        # Uncompress each file ending with ".tar.gz" and put in the custom local repo.
        for compressedFile in $(ls $vagrantRepoItemsDir/*.tar.gz); do
            tar -xzf ${vagrantRepoItemsDir}/${compressedFile} -C $localRepoDir || return 1 
        done 
      
        # Copy each non-compressed file to the custom local repo. 
        for noncompressedFile in $(ls $vagrantRepoItemsDir | grep -v tar.gz); do
            cp -r ${vagrantRepoItemsDir}/${noncompressedFile} $localRepoDir/. || return 1
        done
    fi
    
    createrepo $localRepoDir || return 1 

    # Test custom local repo.
    curl http://localhost/$(basename $localRepoDir)/repodata/repomd.xml &> /dev/null || return 1
}

function setupVanillaAmbari() {
    defaultRepoUrl="http://public-repo-1.hortonworks.com/ambari/centos6/2.x/updates/2.0.1/ambari.repo"
    repoFile=$1
    if [ -z "$repoFile" ]; then
        curl $defaultRepoUrl -o /etc/yum.repos.d/ambari.repo || return 1
        return 0
    fi

    if [ -f "$repoFile" ]; then
        cp $repoFile /etc/yum.repos.d/ambari.repo || return 1
    else
        return 1
    fi

    createCustomLocalRepo || return 1

    yum install -y openssl ambari-server || return 1

    ambari-server setup -s || return 1
    ambari-server start || return 1
}

function setupPivotalAmbari() {
    tarFilePath=$1
    if [ -z "$tarFilePath" ]; then
        return 1
    fi
    
    if [ ! -f "$tarFilePath" ]; then
        return 1
    fi

    setupApache2 || return 1
    
    mkdir /staging || return  1
    chmod a+rx /staging || return 1
    tar -xzf $tarFilePath -C /staging/ || return 1
    
    stagedAmbariDir=$(ls /staging | grep -i AMBARI)
 
    echo ""
    /staging/${stagedAmbariDir}/setup_repo.sh || return 1
    echo ""
 
    curl http://localhost/${stagedAmbariDir}/repodata/repomd.xml &> /dev/null || return 1

    yum install -y openssl ambari-server || return 1

    if [ -f /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz ]; then
        cp /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz /var/lib/ambari-server/resources/jdk-7u67-linux-x64.tar.gz
    fi

    if [ -f /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip ]; then
        cp /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip /var/lib/ambari-server/resources/UnlimitedJCEPolicyJDK7.zip
    fi

    ambari-server setup -s || return 1
    ambari-server start || return 1
}

function setupRaidsAndDataDirs() {
    # Install required packages for setting up each host and installing raid tools.
    yum install -y xfsprogs mdadm unzip ntp ntpdate wget openssl || return 1

    # Get a list of raid devices.
    raid_devices=$(ls /dev/xvd* 2> /dev/null | grep -v xvda 2> /dev/null) 

    # Get the number of raid devices.
    raid_device_count=$(echo "$raid_devices" | wc -l)

    if [ "$raid_device_count" -gt 1 ]; then
        # Set block read ahead on each device for Greenplum.
        for blockdev in $raid_devices; do
            blockdev --setra 16384 $blockdev || return 1
        done

        # Find out whether there is an even or odd amount of devices.
        device_modulo=$(expr $raid_device_count % 2)

        # If there is an even amount of devices AND there are more than 5 devices, create two RAID5 volumes, md0 and md1.
        if [ "$device_modulo" == "0" -a $raid_device_count -gt 5 ]; then

            # Don't create devices if they are already created.
            if [ ! -f /dev/md0 -a ! -f /dev/md0 ]; then
                # We have enough devices to create two RAID 5 volumes
                num_devices_per_raid=$(expr $raid_device_count / 2)

                # Break raid devices up into two even groups.
                device_list_1=$(echo "$raid_devices" | head -${num_devices_per_raid})
                device_list_2=$(echo "$raid_devices" | tail -${num_devices_per_raid})

                # Create both raid devices.
                mdadm --create /dev/md0 --level=5 --chunk 256K --raid-devices=${num_devices_per_raid} $device_list_1 || return 1
                mdadm --create /dev/md1 --level=5 --chunk 256K --raid-devices=${num_devices_per_raid} $device_list_2 || return 1
                mdadm --detail --scan >> /etc/mdadm.conf || return 1
                mkfs.xfs -f /dev/md0 || return 1
                mkfs.xfs -f /dev/md1 || return 1

                # Create data directories.
                mkdir /data1 /data2 || return 1
                chmod 777 /data1 /data2 || return 1

                # Add mount info to fstab.
                echo /dev/md0 /data1 xfs rw,noatime,inode64,allocsize=16m 0 0 >> /etc/fstab || return 1
                echo /dev/md1 /data2 xfs rw,noatime,inode64,allocsize=16m 0 0 >> /etc/fstab || return 1

                # Set scheduler for these devices to deadline.
                echo deadline > /sys/block/md0/queue/scheduler || return 1
                echo deadline > /sys/block/md1/queue/scheduler || return 1
            fi
        else
            # There is only enough devices to create one RAID5 volumes, md0.

            # Don't create device if they are already created.
            if [ ! -f /dev/md0 ]; then
                device_list=$raid_devices

                # Create raid device.
                mdadm --create /dev/md0 --level=5 --chunk 256K --raid-devices=${raid_device_count} $device_list || return 1
                mdadm --detail --scan >> /etc/mdadm.conf || return 1
                mkfs.xfs -f /dev/md0 || return 1

                # Create data directory.
                mkdir /data || return 1
                chmod 777 /data || return 1

                # add mount info to fstab.
                echo /dev/md0 /data xfs rw,noatime,inode64,allocsize=16m 0 0 >> /etc/fstab || return 1

                # Set scheduler for these devices to deadline.
                echo deadline > /sys/block/md0/queue/scheduler || return 1
            fi
        fi
        # Mount new logical disks.
        mount -a || return 1
    fi
}
