#!/bin/bash

# Remove system configuration logs before packaging the image

sed -i '/UUID/d' /etc/sysconfig/network-scripts/ifcfg-e*
sed -i '/HWADDR/d' /etc/sysconfig/network-scripts/ifcfg-e*

# Remove temporary files
rm -rf /tmp/*
rm -rf /tmp/.*

#  Truncate files
> /var/log/wtmp
> /var/log/cron
> /var/log/dmesg
> /var/log/dmesg.old
> /var/log/lastlog
> /var/log/secure
> /var/log/messages
> /var/log/maillog
> /var/log/yum.log
> /etc/resolv.conf

# Remove root history files
rm -f /root/.lesshst
rm -f /root/.bash_history

# Disable root access via ssh + password
rm -f /root/.ssh/authorized_keys
passwd -l root

# Cleanup yum
yum clean all