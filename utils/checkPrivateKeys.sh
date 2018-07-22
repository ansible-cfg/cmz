#!/bin/bash
#
#set -e
#
## Go to current directory, and up one level where the playbooks are located
#cd "$(dirname "$0")"
#cd ../
#
#echo 'Ensure no private keys in vaults'
#set +e
#find -name '*vault*.yml' -exec sh -c "ANSIBLE_LOG_PATH=/dev/null ansible-vault view '{}' | grep -o 'BEGIN RSA PRIVATE KEY'" \; -print | egrep '.*'
#if [[ $? -eq 0 ]]; then
#  echo 'Found private key in vaults'
#  exit 1
#fi
#
#exit 0
