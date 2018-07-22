#!/bin/bash

# Make sure that .ssh & and the id_rsa has correct permissions for vagrant
chmod 700 /home/vagrant/.ssh
chmod 600 /home/vagrant/.ssh/id_rsa