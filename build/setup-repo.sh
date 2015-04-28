#!/bin/bash
# Run during provisioning of master machine, configures a local RPM repository used when installing services.

[ $EUID == 0 ] || exec sudo bash "$0" "$@" # Run as root

LOCAL_REPO_DIR=/var/www/html/phd/

if find /vagrant/artifacts -name 'PHD*' -or -name 'PADS*' -quit &> /dev/null; then 
    echo "Creating local repo"

    rpm --nosignature --replacepkgs -U /vagrant/artifacts/rpms/libxml2-2.7.6-17.el6_6.1.x86_64.rpm 2> /dev/null
    if [ $? == 0 ]; then
        rpm --replacepkgs --nosignature -i \
        /vagrant/artifacts/rpms/mailcap-2.1.31-2.el6.noarch.rpm \
        /vagrant/artifacts/rpms/apr-1.3.9-5.el6_2.x86_64.rpm \
        /vagrant/artifacts/rpms/apr-util-1.3.9-3.el6_0.1.x86_64.rpm \
        /vagrant/artifacts/rpms/apr-util-ldap-1.3.9-3.el6_0.1.x86_64.rpm \
        /vagrant/artifacts/rpms/httpd-tools-2.2.15-39.el6.centos.x86_64.rpm \
        /vagrant/artifacts/rpms/httpd-2.2.15-39.el6.centos.x86_64.rpm \
        /vagrant/artifacts/rpms/python-deltarpm-3.5-0.5.20090913git.el6.x86_64.rpm \
        /vagrant/artifacts/rpms/libxml2-python-2.7.6-17.el6_6.1.x86_64.rpm \
        /vagrant/artifacts/rpms/deltarpm-3.5-0.5.20090913git.el6.x86_64.rpm \
        /vagrant/artifacts/rpms/createrepo-0.9.9-22.el6.noarch.rpm
    else 
        yum install -y httpd createrepo
    fi

    mkdir -p $LOCAL_REPO_DIR
    tar -xvf /vagrant/artifacts/PHD*.tar.gz -C $LOCAL_REPO_DIR
    tar -xvf /vagrant/artifacts/PADS*.tar.gz -C $LOCAL_REPO_DIR
    createrepo $LOCAL_REPO_DIR

    service httpd start
    chkconfig httpd on
else
  echo "Could not find neccesary files to create local repo"
fi
