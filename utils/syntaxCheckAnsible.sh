#!/bin/bash

set -e

# Go to current directory, and up one level where the playbooks are located
cd "$(dirname "$0")"
cd ../

# Run against host types specified in the playbooks
find ./playbooks -maxdepth 1 -name '*.yml'| \
  ANSIBLE_LOG_PATH=/dev/null \
  xargs -n1 ansible-playbook --syntax-check -i "Cmdb,Control,Portal,Web,Repo,yTestRunner,CCloud,localhost"
