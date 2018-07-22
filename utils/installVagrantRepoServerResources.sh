#!/bin/bash

function usage() {
  cat <<Usage

  sudo $(basename $0) [--help -h]

  This script is meant to be run on the local Vagrant-based
  test environment's repo server.
  It installs resources which are expected on the repo server
  during provisioning of other test environment's servers.

  The resources are stored in an unzipped tar archive at
  /vagrant/VagrantRepoServerResources.tar
  The /vargrant directory is Vagrant's standard "shared folder".
  I.e. the HCS-PDO-SRE/mgmtzone_automation/Vagrant folder on your dev box
  mounted into /vagrant on the repo server.

  Resources inside TAR_ARCHIVE are expected to be relative from the
  Linux root directory,i.e.:
    var/automation/backups/CMDB_ro1-cmz-cmdbp-001_2017-11-27_16-42.dump.sql.zip
    var/automation/backups/latest -> CMDB_ro1-cmz-cmdbp-001_2017-11-27_16-42.dump.sql.zip
    var/www/firefox/firefox-47.0.1.tar.bz2
    var/www/ytr2config/ytr2config_FR_DEV.zip
    ...

Usage
}

if [ "$1" = '-h' ] || [ "$1" = '--help' ]
then
    usage
    exit 0
fi


echo "unpacking the tarball into /var/www"
tar -C / -xvkf /vagrant/VagrantRepoServerResources.tar

echo "creating the 'latest' symlink to point to the CMDB backup"
cd /var/automation/backups
rm -f latest
ln -s CMDB_ro1-cmz-cmdbp-001_2017-11-27_16-42.dump.sql.zip latest
