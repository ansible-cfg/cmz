Role Name
=========

Install Jenkins on Control VM

Requirements
------------

  - Java 8 
  - CentOS 7
  - Ansible user SSH key + Ansible vault password defined in credentials (see additional info) 

Role Variables
--------------

TODO

Dependencies
------------

Java 8

Example Playbook
----------------

Include the role in the playbook, see ControlServer.yml

How it works
------------

Install the jenkins from it's yum repository. The Jenkins is configured via init.groovy.d.
Some folders are moved outside of /var/lib/jenkins, as there is noexec set on the mount,
and jenkins fails with it.

The deployment jobs are created via JobDSL, the job configuration is stored in yml.
Final directory structure will be DC/env, which is separated via folders on the jenkins.
(currently this is in progress)

What is currently configured:
  - Installs plugins
  - CSRF Protection (security)
  - Disable old Java agents (security)
  - Adds the bitbucket svc user ssh key
  - Remove CLI remoting (security)
  - Sets the proxy
  - Creates a seed job

TODO:
  - Setup authorization security via LDAP (currently it's NONE)
  - Create the seed job from groovy instead of copying an XML
  - Setup HTTPS properly
  - Groovy scripts need some meaningful logging set to

Vagrant access
--------------
Open 127.0.0.1:160443 in browser, or vagrant-cmz-ctrlp-001.local:16443 if configured
in etc/hosts

Additional info
---------------
When running the SeedJob the first time OR it's code gets modified, a "script approve" is needed
on the Jenkins UI ("Script not approved" can be seen in the build output).
This can be found under "Configuration/In-process script approval"

For ansible to work, you have to manually add the ansible service user SSH key
and the vault password to the credentials store. The SSH key's ID should be "ansible_ssh_key",
and the vault password ID should be "ansible_vault_passwd" (secret text type of credential)

For Monitoring-Config Job to run, you need to add following things into jenkins credentials 
1.) Git Reposioty ssh-key, ID should be "monitoring_scm_ssh_key" key value will be found in our PassVault.
2.) The ansible service user SSH key with ID "monitoring_ansible_ssh_key" and user is "svc_[DC]ansible_mon" can be found in home dir of the service user.
3.) monitoring_ansible_vault_passwd value will be found in our PassVault.

Note that on Vagrant a "Reverse Proxy broken" notify appears, this is due to the portforwarded
setup. The browser wants to do a check against the Jenkins URL without the port, so it fails.

License
-------

SAP

Author Information
------------------

CSESRE SRE Team
