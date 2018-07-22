#!/bin/bash

# By default go to git dir after login with vagrant user
bashrc_file='/home/vagrant/.bashrc'
git_dir='/home/vagrant/git_hcs-pdo-sre/mgmtzone_automation'
cd_command="[[ -d '$git_dir' ]] && cd '$git_dir'"
if ! grep -Fsq "$cd_command" "$bashrc_file"; then
  echo "$cd_command" >> "$bashrc_file"
fi
