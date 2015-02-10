# vim: set ft=ruby:

# Generate ssh key
Dir.chdir(File.dirname(__FILE__)) do 
    `ssh-keygen -t rsa -f private_key -N ''` unless File.exists? 'private_key'
end

Vagrant.configure(2) do |config|
    config.vm.box = 'chef/centos-6.5'

    config.hostmanager.enabled = true
    config.hostmanager.manage_host = true

    config.hostmanager.ip_resolver = proc do |vm, resolving_vm|
        begin
            buffer = '';
            vm.communicate.execute("/sbin/ifconfig") do |type, data|
              buffer += data if type == :stdout
            end

            ips = []
            ifconfigIPs = buffer.scan(/inet addr:(\d+\.\d+\.\d+\.\d+)/)
            ifconfigIPs[0..ifconfigIPs.size].each do |ip|
                ip = ip.first

                next unless system "ping -c1 -t1 #{ip} > /dev/null"

                ips.push(ip) unless ips.include? ip
            end

            ips.first
        rescue StandardError => exc
            puts exc
        end
    end

    config.vm.define 'master', primary: true do |node|
        node.vm.network 'private_network', type: :dhcp
        node.vm.hostname = "master.ambaricluster.local"

        node.vm.provider 'virtualbox' do |v|
            v.memory = 2048
        end

        node.vm.synced_folder '1.0.0.zData', '/var/lib/ambari-server/resources/stacks/HDP/1.0.0.zData', create: true
        
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