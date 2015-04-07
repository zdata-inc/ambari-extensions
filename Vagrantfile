# vim: set ft=ruby:

require 'json'

# ================================================================================
# Variables
# ================================================================================
# 
# Create a hash of variables for use throughout the rest of the vagrant file.
# When creating the machines for the first time the variables will be stored in
# the variablesFile for use during subsequent calls to the vagrant command.
# When the machines are destroyed, this file is also removed.

variablesFile = File.join File.dirname(__FILE__), '.vagrant', 'ambari-variables'

params = {
    'master_count' => (ENV['AMBARI_MASTERS'] || 1).to_i,
    'slave_count' => (ENV['AMBARI_SLAVES'] || 1).to_i
}

# Overwrite parameters with those stored, fail silently
params.merge!(JSON.parse(IO.read(variablesFile))) if File.exists? variablesFile rescue StandardError


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
    config.vm.box = 'chef/centos-6.5'


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
    # Triggers
    # ================================================================================

    config.trigger.after :up do
        # Save variables for subsequent calls
        File.open(variablesFile, 'w') do |file|
            file.write(JSON.generate(params))
        end
    end

    config.trigger.after :destroy do
        File.delete variablesFile if File.exists? variablesFile
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

            node.vm.synced_folder 'src', '/var/lib/ambari-server/resources/stacks/HDP/9.9.9.zData', create: true

            node.vm.provision 'shell', privileged: false, inline: 'echo "export PATH=/vagrant/build:$PATH" >> ~/.bashrc'
            node.vm.provision 'shell', path: 'build/bootstrap.sh'
            node.vm.provision 'shell', path: 'build/bootstrap-master.sh'
            node.vm.provision :reload
        end
    end

    params['slave_count'].times.each do |i|
        i += 1

        config.vm.define "slave#{i}" do |node|
            node.vm.network 'private_network', type: :dhcp
            node.vm.hostname = "slave#{i}.ambaricluster.local"

            node.vm.provider 'virtualbox' do |v|
                v.memory = 8192
            end

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

            node.vm.provision 'shell', privileged: false, inline: 'echo "export PATH=/vagrant/build:$PATH" >> ~/.bashrc'
            node.vm.provision 'shell', path: 'build/bootstrap.sh'
            node.vm.provision 'shell', path: 'build/bootstrap-slave.sh'
            node.vm.provision :reload
        end
    end
end