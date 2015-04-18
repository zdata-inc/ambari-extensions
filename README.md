zData Ambari Stack
==================
Ambari is a tool which makes provisioning, managing, and monitoring of Apache Hadoop deployments easy.  zData's stack builds atop Ambari to provide easy deployment and management of HAWQ, Chorus, and soon other Pivotal technologies.

[Visit the project's documentation for quick start guides and more information.](http://zdata-inc.github.io/ambari-stack)


Getting started with Vagrant
----------------------------

1. Requires the following plugins: vagrant-hostmanager, vagrant-reload, vagrant-triggers

    ```shell
    vagrant plugin install vagrant-hostmanager
    vagrant plugin install vagrant-reload
    vagrant plugin install vagrant-triggers

    vagrant plugin install vagrant-aws # To provision on AWS
    ```

2. Create boxes with Virtualbox

    ```shell
    AMBARI_SLAVES=5 vagrant up # Bring up master, slave1, slave2, ..., slave5
    AMBARI_SLAVES=1 vagrant up # Bring up master and slave1
    AMBARI_SLAVES=0 vagrant up # Bring up just master
    ```

3. Connect, vms created: master, slave0, slave1

    ```
    master.ambaricluster.local
    slave0.ambaricluster.local
    slave1.ambaricluster.local

    vagrant ssh master
    vagrant ssh slave0
    vagrant ssh slave1
    ```

### Additional steps to deploy to AWS:

1. Install a dummy box:

    ```shell
    vagrant box add dummy https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box
    ```

2. Configure Vagrant with your unique Amazon access key and secret.
    Creating a user Vagrantfile in `~/.vagrant.d/Vagrantfile` with:

    ```ruby
    Vagrant.configure('2') do |config|
        config.vm.provider :aws do |aws, override|
            aws.access_key_id = ENV['AWS_KEY']
            aws.secret_access_key = ENV['AWS_SECRET']
        end
    end
    ```

    Add environmental variables with your AWS_KEY and AWS_SECRET in your `~/.bashrc`:

    ```shell
    export AWS_KEY="THEKEY"
    export AWS_SECRET="THESECRET"
    ```

3. Configure Vagrant with a keypair it can use to communicate with the created boxes.
    Generate a new keypair.  In your user Vagrantfile add the following lines in the `config.vm.provider :aws` block:

    ```ruby
    aws.keypair_name = 'vagrant'
    override.ssh.private_key_path = '~/.ssh/aws-vagrant'
    ```

    The variable `keypair_name` should be the name of the keypair on AWS, the variable `private_key_path` should be the path to the private key on your local computer.

    Your user Vagrantfile should now look like:

    ```ruby
    Vagrant.configure('2') do |config|
        config.vm.provider :aws do |aws, override|
            aws.access_key_id = ENV['AWS_KEY']
            aws.secret_access_key = ENV['AWS_SECRET']
            aws.keypair_name = 'vagrant'
            override.ssh.private_key_path = '~/.ssh/aws-vagrant'
        end
    end
    ```

4. Create the boxes on AWS

    ```shell
    AMBARI_SLAVES=5 vagrant up --provider=aws --no-parallel
    vagrant hostmanager
    ```

More information about getting started with Ambari using vagrant [is available here](http://zdata-inc.github.io/ambari-stack/getting-setup/with-vagrant.html).

What Services Do Not Do
-----------------------
### Greenplum

 - Does not automatically create or setup XFS filesystem.
 - Does not specifiy an IO scheduler of deadline.
 - Does not configure read-ahead.
 - Does not disable transparent hugepage.

Retrieve Artifacts
------------------

To install HAWQ you will need some files from Pivotal.
You can find these files at https://network.pivotal.io/products/pivotal-hd.  Create an account if you don't have one already, and download `Pivotal HD 2.1.0` and `PHD 2.1.0: Pivotal HAWQ 1.2.1.0`.  Place the downloaded files in the artifacts folder located in the project root.