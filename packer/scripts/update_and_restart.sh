#!/bin/bash

# Update all the packages on the OS, then reboots to get kernel changes applied in order to get the correct kernel-headers installed

yum update -y
reboot
