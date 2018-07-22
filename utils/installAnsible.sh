#!/bin/bash

function install_via_os () {
    echo "installing Ansible via OS package manager"
    sudo yum -y install 'python-2*' 'ansible-2.*'
}

function install_via_pip () {
    echo "installing Ansible via pip"
    sudo yum -y install ca-certificates curl vim 'python-2*' 'python-devel-2*' libffi-devel git
    sudo yum -y install cscope ctags diffstat gcc gettext indent intltool libtool
    pip --version &>/dev/null  || { curl -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && sudo /bin/bash -c 'umask 0022; python /tmp/get-pip.py; umask 0027'; }
    ansible --version &>/dev/null  || { sudo /bin/bash -c 'umask 0022; pip install ansible==2.3.1.0 yaml; umask 0027'; }
}

install_via_os

cat <<NextSteps

Refer to the documentation on
https://wiki.hybris.com/display/MSPIPS/SRE+Management+Zone+Automation
for next steps and how to run Ansible.

NextSteps
