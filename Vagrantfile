# vim: set ft=ruby:

slaveCount = ENV['AMBARI_SLAVES'].to_i || 1

# Generate ssh key
Dir.chdir(File.dirname(__FILE__)) do
    `ssh-keygen -t rsa -f private_key -N ''` unless File.exists? 'private_key'
end

Vagrant.configure(2) do |config|
    config.vm.box = 'chef/centos-6.5'

    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true
    config.hostmanager.ip_resolver = proc do |vm, resolving_vm|
        return if vm.id.nil?

        buffer = '';
        vm.communicate.execute('/sbin/ifconfig eth1 | grep "inet"') do |type, data|
            buffer += data if type == :stdout
        end

        buffer.split("\n").first[/(\d+\.\d+\.\d+\.\d+)/, 1]
    end

    config.vm.define 'master', primary: true do |node|
        node.vm.network 'private_network', type: :dhcp
        node.vm.hostname = "master.ambaricluster.local"

        node.vm.provider 'virtualbox' do |v|
            v.memory = 4096
        end

        node.vm.synced_folder 'src', '/var/lib/ambari-server/resources/stacks/HDP/9.9.9.zData', create: true

        node.vm.provision 'shell', privileged: false, inline: 'echo "export PATH=/vagrant/build:$PATH" >> ~/.bashrc'
        node.vm.provision 'shell', path: 'build/bootstrap.sh'
        node.vm.provision 'shell', path: 'build/bootstrap-master.sh'
        node.vm.provision :reload
        node.vm.provision 'hostmanager'
    end

    slaveCount.times.each do |i|
        i += 1
        config.vm.define "slave#{i}" do |node|
            node.vm.network 'private_network', type: :dhcp
            node.vm.hostname = "slave#{i}.ambaricluster.local"

            node.vm.provider 'virtualbox' do |v|
                v.memory = 4096
            end

            node.vm.provision 'shell', privileged: false, inline: 'echo "export PATH=/vagrant/build:$PATH" >> ~/.bashrc'
            node.vm.provision 'shell', path: 'build/bootstrap.sh'
            node.vm.provision 'shell', path: 'build/bootstrap-slave.sh'
            node.vm.provision :reload
            node.vm.provision 'hostmanager'
        end
    end
end
