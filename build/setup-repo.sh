#!/bin/bash
[ $EUID == 0 ] || exec sudo bash "$0" "$@"

LOCAL_REPO_DIR=/var/www/html/phd/

if find /vagrant/artifacts -name 'PHD*' -or -name 'PADS*' -quit &> /dev/null; then 
  echo "Creating local repo"

  yum install -y httpd createrepo

  mkdir -p $LOCAL_REPO_DIR
  tar -xvf PHD*.tar.gz -C $LOCAL_REPO_DIR
  tar -xvf PADS*.tar.gz -C $LOCAL_REPO_DIR
  createrepo $LOCAL_REPO_DIR

  service httpd start
  chkconfig httpd on
else
  echo "Could not find neccesary files to create local repo"
fi
