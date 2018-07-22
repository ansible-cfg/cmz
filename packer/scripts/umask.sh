#!/bin/bash

# Set restricting umask
sed -i 's#^\([[:space:]]*\)umask[[:space:]][[:digit:]]*#\1umask 027#g' /etc/profile
sed -i 's#^\([[:space:]]*\)umask[[:space:]][[:digit:]]*#\1umask 027#g' /etc/bashrc

