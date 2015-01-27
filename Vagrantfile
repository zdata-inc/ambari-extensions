# -*- mode: ruby -*-
# vi: set ft=ruby :

# Generate ssh key
`ssh-keygen -t rsa -f private_key -N ''` unless File.exists? 'private_key'

Vagrant.configure(2) do |config|
    config.vm.box = 'chef/centos-6.5'

    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true

    config.hostmanager.ip_resolver = proc do |vm, resolving_vm|
        buffer = '';
        vm.communicate.execute("/sbin/ifconfig") do |type, data|
          buffer += data if type == :stdout
        end

        ips = []
        ifconfigIPs = buffer.scan(/inet addr:(\d+\.\d+\.\d+\.\d+)/)
        ifconfigIPs[0..ifconfigIPs.size].each do |ip|
            ip = ip.first
            next if ip == '127.0.0.1'
            next if ip.start_with? '10.'

            ips.push(ip) unless ips.include? ip
        end

        ips.first
    end

    config.vm.define 'master', primary: true do |node|
        node.vm.network 'private_network', type: :dhcp
        node.vm.hostname = "master.ambaricluster.local"

        node.vm.provider 'virtualbox' do |v|
            # v.memory = 2048
        end

        # node.vm.synced_folder 
        
        node.vm.provision 'shell', path: 'vagrant/bootstrap.sh'
        node.vm.provision 'shell', path: 'vagrant/bootstrap-master.sh'
        config.vm.provision :hostmanager
    end

    2.times.each do |i|
        config.vm.define "slave#{i}" do |node|
            node.vm.network 'private_network', type: :dhcp
            node.vm.hostname = "slave#{i}.ambaricluster.local"

            node.vm.provision 'shell', path: 'vagrant/bootstrap.sh'
            node.vm.provision 'shell', path: 'vagrant/bootstrap-slave.sh'
            config.vm.provision :hostmanager
        end
    end
end