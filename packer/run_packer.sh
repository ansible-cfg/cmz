#!/bin/bash

cd `dirname $0`
echo "Removing SSH key if exists"
rm -f  ./http/id_rsa
rm -f  ./http/id_rsa.pub
echo "Generating temporary SSH keys"
ssh-keygen -N "" -f ./http/id_rsa
packer build centos7.json

