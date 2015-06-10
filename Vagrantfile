# vim: set ft=ruby:

require 'json'

cached_repositories=%w(HDP-2.2)

# ================================================================================
# Variables
# ================================================================================
#
# Retrieve the vagrant-env variables used to customize the local ambari environment.

variablesFile = [
    File.join(File.dirname(__FILE__), 'vagrant-env.conf'),
    File.join(File.dirname(__FILE__), 'vagrant-env.conf.sample')
]

abort 'Failed to find configuration file.' if variablesFile.nil?

variablesFile = variablesFile.find { |path| File.exists? path }
params = JSON.parse(IO.read(variablesFile))

# ================================================================================
# Shared SSH Key
# ================================================================================
#
# Create an SSH key that can be shared between all the machines.
# This key will be used by Ambari during registration step.

Dir.chdir(File.dirname(__FILE__)) do
    Dir.mkdir 'keys' unless File.exists? 'keys'
    `ssh-keygen -t rsa -f keys/private_key -N ''` unless File.exists? 'keys/private_key'
end

Vagrant.configure(2) do |config|
    config.vm.box_url = 'https://s3-us-west-2.amazonaws.com/zdata-vagrant/boxes/vagrant-centos-66-zdata.box'
    config.vm.box = 'vagrant-centos-66-zdata'
    vm_centos_major_version = '6'
    vm_arch = 'x86_64'


    # ================================================================================
    # Host Manager configuration
    # ================================================================================
    #
    # The HostManager plugin is used to configure each of the machines to be able to communicate
    # to the others via their hostname, even when the IP address are dynamic.

    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true
    config.hostmanager.ip_resolver = proc do |vm, resolving_vm|
        return if vm.id.nil?

        begin
            buffer = '';
            vm.communicate.execute("/sbin/ifconfig | grep -Po 'inet\s+.+?:.+?\s+' | grep -v '127.0.0.1'") do |type, data|
                buffer += data if type == :stdout
            end

            buffer.scan(/(\d+\.\d+\.\d+\.\d+)/).to_a.last[0]
        rescue StandardError
            nil
        end
    end

    # ================================================================================
    # Providers
    # ================================================================================

    config.vm.provider :aws do |aws, override|
        aws.ami = 'ami-d47c57bc'

        override.vm.box = 'dummy'
        override.ssh.username = 'root'

        # Use AWS specific service to retrieve public IP for the machine.
        override.hostmanager.ip_resolver = proc do |vm, resolving_vm|
            return if vm.id.nil?

            buffer = ''
            vm.communicate.execute("curl --connect-timeout 5 http://169.254.169.254/latest/meta-data/public-ipv4") do |type, data|
                buffer += data if type == :stdout
            end

            buffer.strip
        end

        # Only sync specific folders, otherwise we'd be rsyncing GBs of data.
        override.vm.synced_folder ".", "/vagrant", disabled: true
        override.vm.synced_folder "build", "/vagrant/build", create: true
        override.vm.synced_folder "keys", "/vagrant/keys", create: true
    end


    config.vm.provider 'virtualbox' do |v|
        v.memory = 4096
    end


    # ================================================================================
    # Machines
    # ================================================================================
    params['master_count'].times.each do |i|
        i += 1

        # Only display number for master2 and after.
        displayedI = (i == 1) ? "" : i
        config.vm.define "master#{displayedI}", primary: i == 1 do |node| #TODO
            node.vm.network 'private_network', type: :dhcp

            node.vm.hostname = "master#{displayedI}.ambaricluster.local"
            node.hostmanager.aliases = ["master#{displayedI}", "master#{i}"]

            node.vm.provider 'aws' do |aws, override|
                aws.tags = {
                    'Name' => "Ambari Testing - Master #{i}"
                }

                # Force set hostname on ec2 instances
                override.vm.provision :shell, inline: <<-EOF
                    echo '#{node.vm.hostname}' > /etc/hostname;
                    sed -i 's/^127\\.0\\.0\\.1.*$/127.0.0.1 localhost/' /etc/hosts
                    sed -i 's/^HOSTNAME=.*$/HOSTNAME=#{node.vm.hostname}/' /etc/sysconfig/network
                    hostname `cat /etc/hostname`
                EOF
            end

            node.vm.synced_folder 'src', '/var/lib/ambari-server/resources/stacks/zData/9.9.9', create: true

            cached_repositories.each do |repo|
                node.vm.synced_folder "artifacts/cache/master-#{i}/#{repo}", "/var/cache/yum/#{vm_arch}/#{vm_centos_major_version}/#{repo}", create: true
            end

            node.vm.provision 'shell', path: 'build/bootstrap.sh'
            node.vm.provision 'shell', path: 'build/bootstrap-master.sh'
            node.vm.provision 'shell', privileged: false, inline: 'echo "export PATH=/vagrant/build:$PATH" >> ~/.bashrc'
            node.vm.provision :reload
        end
    end

    params['slave_count'].times.each do |i|
        i += 1

        config.vm.define "slave#{i}" do |node|
            node.vm.network 'private_network', type: :dhcp
            node.vm.hostname = "slave#{i}.ambaricluster.local"
            node.hostmanager.aliases = ["slave#{i}"]

            node.vm.provider 'aws' do |aws, override|
                aws.tags = {
                    'Name' => "Ambari Testing - Slave #{i}"
                }

                # Force set hostname on ec2 instances
                override.vm.provision :shell, inline: <<-EOF
                    echo '#{node.vm.hostname}' > /etc/hostname;
                    sed -i 's/^127\\.0\\.0\\.1.*$/127.0.0.1 localhost/' /etc/hosts
                    sed -i 's/^HOSTNAME=.*$/HOSTNAME=#{node.vm.hostname}/' /etc/sysconfig/network
                    hostname `cat /etc/hostname`
                EOF
            end

            cached_repositories.each do |repo|
                node.vm.synced_folder "artifacts/cache/slave-#{i}/#{repo}", "/var/cache/yum/#{vm_arch}/#{vm_centos_major_version}/#{repo}", create: true
            end

            node.vm.provision 'shell', path: 'build/bootstrap.sh'
            node.vm.provision :reload
        end
    end
end

