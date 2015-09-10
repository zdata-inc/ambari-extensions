#!/bin/bash

defaultRepoUrl="http://public-repo-1.hortonworks.com/ambari/centos6/2.x/updates/2.0.1/ambari.repo"

if [ "$EUID" != 0 ]; then
        echo "Please run as root user"
        exit 1
fi

function error() {
    if [ ! -z "$1" ]; then
        >&2 echo $1
    fi

    return 1
}

function installDesiredPackages() {
    yum install -y vim screen || { error "Could not install support packages." || return 0; }
}

# Vagrant specific
function vagrantSetupHostsFile() {
    # Fixes issue #1
    sed -i "s;^127\.0\.0\.1\(.*\);127.0.0.1 localhost;" /etc/hosts || \
        { error "Failed to modify the guest machine mapping in /etc/hosts" || return $?; }
}

# Vagrant specific
function vagrantCreateSharedKeys () {
    if [ ! -d ~/.ssh ]; then
        mkdir ~/.ssh || \
            { error "Failed to make guest machine .ssh directory." || return $?; }
    fi

    (cat /vagrant/keys/private_key.pub >> ~/.ssh/authorized_keys && \
        cp /vagrant/keys/private_key ~/.ssh/id_rsa && \
        cp /vagrant/keys/private_key.pub ~/.ssh/id_rsa.pub) || \
        { error 'Failed to add shared keys to guest machine.' || return $?; }
}

function setupApache2() {
    service httpd status &> /dev/null
    if [ $? -ne 0 ]; then
        yum install -y httpd || \
            { error 'Failed to install httpd.' || return $?; }
        service httpd start || \
            { error 'Failed to start httpd.' || return $?; }
        chkconfig httpd on || \
            { error 'Failed to set httpd to start on boot.' || return $?; }
    fi
}

function setupNTPD() {
    yum install -y ntp ntpdate || \
        { error 'Failed to install ntp.' || return $?; }

    # Configure and sync up time. Make sure ntpd starts up on restart.
    (service ntpd stop && \
        ntpdate pool.ntp.org && \
        service ntpd start && \
        chkconfig ntpd on) || \
        { error 'Failed to configure NTP.' || return $?; }
}

function disableFirewall() {
    # Turn off iptables and make sure it doesn't boot up on restart.
    (service iptables stop && \
        chkconfig iptables off) || \
        { error 'Failed to disable iptables.' || return $?; }
}

function removeMemoryLimitationOnUsers() {
    # Remove memory limitation on users.
    sed -i '/\*.*.soft.*.nproc.*.1024.*$/d' /etc/security/limits.d/90-nproc.conf || \
        { error 'Failed to reconfigure limits.' || return $?; }
}

function setSystemScheduling() {
    sed -i '/kernel/ s/$/ elevator=deadline/' /boot/grub/grub.conf || \
        { error 'Failed to modify system harddisk scheduling.' || return 0; }
}

function disableTHP() {
    (sed -i '/kernel/ s/$/ transparent_hugepage=never/' /boot/grub/grub.conf && \
        echo never > /sys/kernel/mm/transparent_hugepage/enabled) || \
        { error 'Failed to disable transparent hugepages.' || return 0; }
}

function disableSelinux() {
    # Turn off SELINUX permanently and temporarily.
    (sed -i 's/^SELINUX=.*$/SELINUX=disabled/' /etc/selinux/config && \
        echo 0 > /selinux/enforce) || \
        { error 'Failed to disable SELinux.' || return $?; }
}

function configureSSH() {
    # Configure sshd to enable RootLogin and PasswordAuthentication, then restart sshd.
    # NOTE - This may not be required if there is a common key on mdw that can ssh into other hosts before the Greenplum installer runs.
    sed -i -e 's/#\?PermitRootLogin.*$/PermitRootLogin yes/g' -e 's/#\?PasswordAuthentication .*$/PasswordAuthentication yes/' /etc/ssh/sshd_config || \
        { error 'Failed to reconfigure sshd.  Should allow root and password logins.' || return $?; }
    service sshd restart || \
        { error 'Failed to restart sshd.' || return $?; }
}

function setupAmbariExtensions() {
    # Download Ambari zData Extensions and install it.
    pushd /tmp
    currentUrl=https://s3-us-west-2.amazonaws.com/zdata-ambari/releases/zdata-ambari-stack-52c1dbb0.tar.gz
    curl $currentUrl -o zdata-ambari-stack.tar.gz || \
        { error 'Failed to download zData Ambari Extensions' || return 0; }
    (tar -xzf zdata-ambari-stack*.tar.gz &&
        cd zdata-ambari-stack* && make install) || \
        { error 'Failed to install zData Ambari Extensions' || return 0; }
    popd
}

function moveItemsInRepo() {
    if [ -f "$vagrantRepoItemsDir" ]; then
        # Uncompress each file ending with ".tar.gz" and put in the custom local repo.
        for compressedFile in $(ls $vagrantRepoItemsDir/*.tar*); do
            tar -xzf ${vagrantRepoItemsDir}/${compressedFile} -C $localRepoDir || \
                { error "Failed to extract ${vagrantRepoItemsDir}/${compressedFile} while creating local repo." || return $?; }
        done

        # Copy each non-compressed file to the custom local repo.
        for noncompressedFile in $(ls $vagrantRepoItemsDir | grep -v tar); do
            cp -r ${vagrantRepoItemsDir}/${noncompressedFile} $localRepoDir/. || \
                { error "Failed to copy ${vagrantRepoItemsDir}/${noncompressedFile} to $localRepoDir while creating local repo." || return $?; }
        done
    fi
}

function createCustomLocalRepo() {
    # Directory to contain custom local repo.
    localRepoDir=/var/www/html/ambari-extensions
    # Directory of artifacts that should be put into custom local repo (optional).
    vagrantRepoItemsDir=/vagrant/artifacts/repoItems

    setupApache2 || \
        { error 'Failed to setup httpd.' || return $?; }

    yum install -y createrepo || \
        { error 'Failed to install createrepo package.' || return $?; }
    mkdir -p $localRepoDir || \
        { error "Failed to create $localRepoDir" || return $?; }

    moveItemsInRepo || \
        { error 'Failed to move items into repository.' || return $?; }

    createrepo $localRepoDir || \
        { error "Failed to create localrepo at $localRepoDir" || return $?; }

    # Test custom local repo.
    curl http://localhost/$(basename $localRepoDir)/repodata/repomd.xml &> /dev/null || \
        { error "Local repository $localRepoDir was created, but is not accessible." || return $?; }
}

function copyAmbariArtifacts() {
    if [ -f /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz ]; then
        \cp -n /vagrant/artifacts/jdk-7u67-linux-x64.tar.gz /var/lib/ambari-server/resources/jdk-7u67-linux-x64.tar.gz
    fi

    if [ -f /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip ]; then
        \cp -n /vagrant/artifacts/UnlimitedJCEPolicyJDK7.zip /var/lib/ambari-server/resources/UnlimitedJCEPolicyJDK7.zip
    fi
}

function setupVanillaAmbari() {
    repoFile=$1
    if [ -z "$repoFile" -o ! -e "$repoFile" ]; then
        curl $defaultRepoUrl -o /etc/yum.repos.d/ambari.repo || \
            { error 'Failed to fetch default Ambari repository.' || return $?; }
    fi

    if [ -e "$repoFile" ]; then
        cp $repoFile /etc/yum.repos.d/ambari.repo || \
            { error 'Failed to install Ambari repository.' || return $?; }
    fi

    createCustomLocalRepo || \
        { error 'Failed to create custom local repository.' || return $?; }

    yum install -y openssl ambari-server || \
        { error 'Failed to install ambari server package.' || return $?; }

    copyAmbariArtifacts || \
        { error 'Failed to copy Ambari artifacts.' || return $?; }

    ambari-server setup -s || \
        { error 'Failed to setup ambari server.' || return $?; }
    ambari-server start || \
        { error 'Failed to start Ambari server.' || return $?; }
}

function setupPivotalSoftwareSpecificRepo() {
    tarFilePath=$1
    [ -z "$tarFilePath" ] && { error 'No Pivotal Software repository given.' || return $?; }
    [ ! -f "$tarFilePath" ] && { error "Could not find Pivotal repository at $tarFilePath" || return $?; }

    mkdir -p /staging
    chmod a+rx /staging
    tar -xzf $tarFilePath -C /staging/ || \
        { error "Failed to extract $tarFilePath while creating Pivotal repository." || return $?; }

    stagedDir=""
    for dir in $(ls /staging); do
        search=$(echo $tarFilePath | grep $dir)
        if [ -n "$search" ]; then
            stagedDir=$dir
        fi
    done

    setupApache2 || \
        { error 'Failed to setup httpd.' || return $?; }

    echo
    /staging/${stagedDir}/setup_repo.sh || \
        { error "Pivotal /staging/$stagedDir/setup_repo.sh failed." || return $?; }
    echo

    curl http://localhost/$stagedDir/repodata/repomd.xml &> /dev/null || \
        { error "Pivotal local repository $stagedDir created, but is not accessible." || return $?; }
}

function setupPivotalAmbari() {
    setupPivotalSoftwareSpecificRepo $1 || \
        { error 'Failed to setup Pivotal software repository.' || return $?; }

    yum install -y openssl ambari-server || \
        { error 'Failed to install ambari server package.' || return $?; }

    copyAmbariArtifacts || \
        { error 'Failed to copy Ambari Artifacts.' || return $?; }

    ambari-server setup -s || \
        { error 'Failed to setup Pivotal Ambari.' || return $?; }
    ambari-server start || \
        { error 'Failed to start Pivotal Ambari.' || return $?; }
}

function setupRaidsAndDataDirs() {
    # Install required packages for setting up each host and installing raid tools.
    yum install -y xfsprogs mdadm unzip ntp ntpdate wget openssl || \
        { error 'Failed to install prerequisite packages.' || return $?; }

    # Get a list of raid devices.
    raid_devices=$(ls /dev/xvd* 2> /dev/null | grep -v xvda 2> /dev/null)

    # Get the number of raid devices.
    raid_device_count=$(echo "$raid_devices" | wc -l)

    if [ "$raid_device_count" -gt 1 ]; then
        # Set block read ahead on each device for Greenplum.
        for blockdev in $raid_devices; do
            blockdev --setra 16384 $blockdev || \
                { error "Failed to set read ahead on disk ${blockdev}." || return $?; }
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
                mdadm --create /dev/md0 --level=5 --chunk 256K --raid-devices=${num_devices_per_raid} $device_list_1 || \
                    { error "Failed to create raid of disks ${device_list_1}." || return $?; }
                mdadm --create /dev/md1 --level=5 --chunk 256K --raid-devices=${num_devices_per_raid} $device_list_2 || \
                    { error "Failed to create raid of disks ${device_list_2}." || return $?; }
                mdadm --detail --scan >> /etc/mdadm.conf || \
                    { error 'Failed to save details of raids to /etc/mdadm.conf.' || return $?; }
                mkfs.xfs -f /dev/md0 || \
                    { error 'Failed to create filesystem for raid /dev/md0.' || return $?; }
                mkfs.xfs -f /dev/md1 || \
                    { error 'Failed to create filesystem for raid /dev/md1.' || return $?; }

                # Create data directories.
                (mkdir /data1 /data2 && \
                    chmod 777 /data1 /data2) || \
                    { error 'Failed to make data directories.' || return $?; }

                # Add mount info to fstab.
                (echo /dev/md0 /data1 xfs rw,noatime,inode64,allocsize=16m 0 0 >> /etc/fstab && \
                    echo /dev/md1 /data2 xfs rw,noatime,inode64,allocsize=16m 0 0 >> /etc/fstab) || \
                    { error 'Failed to write raid details to /etc/fstab.' || return $?; }

                # Set scheduler for these devices to deadline.
                (echo deadline > /sys/block/md0/queue/scheduler && \
                    echo deadline > /sys/block/md1/queue/scheduler) || \
                    { error 'Failed to set raid scheduler to deadline.' || return 0; }
            fi
        else
            # There is only enough devices to create one RAID5 volumes, md0.

            # Don't create device if they are already created.
            if [ ! -f /dev/md0 ]; then
                device_list=$raid_devices

                # Create raid device.
                mdadm --create /dev/md0 --level=5 --chunk 256K --raid-devices=${raid_device_count} $device_list || \
                    { error "Failed to create raid of disks ${raid_list}." || return $?; }
                mdadm --detail --scan >> /etc/mdadm.conf || \
                    { error 'Failed to save details of raid to /etc/mdadm.conf.' || return $?; }
                mkfs.xfs -f /dev/md0 || \
                    { error 'Failed to create filesystem for raid /dev/md0.' || return $?; }

                # Create data directory.
                (mkdir /data && \
                    chmod 777 /data) || \
                    { error 'Failed to make data directories.' || return $?; }

                # add mount info to fstab.
                echo /dev/md0 /data xfs rw,noatime,inode64,allocsize=16m 0 0 >> /etc/fstab || \
                    { error 'Failed to write raid details to /etc/fstab.' || return $?; }

                # Set scheduler for these devices to deadline.
                echo deadline > /sys/block/md0/queue/scheduler || \
                    { error 'Failed to set raid scheduler to deadline.' || return 0; }
            fi
        fi
        # Mount new logical disks.
        mount -a || \
            { error 'Failed to remount all devices.' || return $?; }
    fi
}
