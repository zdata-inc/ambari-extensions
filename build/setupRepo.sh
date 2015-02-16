#!/bin/bash
[ $EUID == 0 ] || exec sudo bash "$0" "$@"

PHD_DOWNLOAD_PATH=/vagrant/artifacts/PHD-2.1.0.0-175.tar.gz
PADS_DOWNLOAD_PATH=/vagrant/artifacts/PADS-1.2.1.0-10335.tar.gz
LOCAL_REPO_DIR=/var/www/html/phd/
PHD_DIR=PHD-2.1.0.0-175

if [ -f "$PHD_DOWNLOAD_PATH" -a -f "$PADS_DOWNLOAD_PATH" ]; then 
  echo "Creating local repo"
  yum install -y httpd createrepo
  mkdir -p $LOCAL_REPO_DIR
  tar -xvf $PHD_DOWNLOAD_PATH -C $LOCAL_REPO_DIR
  tar -xvf $PADS_DOWNLOAD_PATH -C $LOCAL_REPO_DIR
  createrepo $LOCAL_REPO_DIR
  service httpd start
  chkconfig httpd on
else
  echo "Could not find neccesary files to create local repo"
fi
