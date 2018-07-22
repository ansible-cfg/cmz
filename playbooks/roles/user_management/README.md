This role:
* creates service user accounts incl. ssh keys and sudo configuration
* installs additional keys for the Ansible service user to ssh into git and scp CMDB backups
  REMEMBER TO STORE THE NEW PUBLIC SSH KEY IN THE GIT REPO CONFIGURATION IF YOU CHANGE SSH KEYS FOR GIT ACCESS

*** MAKE SURE THIS ROLE DOES NOT INTERFERE WITH THE SERVICE USERS MAINTAINED BY INFRASTRUCTURE ***
In Hybris datacenters, users and service users are managed and owned by team Infrastructure!
This role will skip most of its tasks in Hybris datacenters.

It will mostly operate on SRE datacenters, our own datacenters for testing, e.g. in Vagrant or CCloud.
Creating service users must only happen for SRE's test servers.


This role includes all the logic as to which accounts are created on which hosts.
I must be the only source for that logic.
No other playbook must implement that logic.

Other plays should install the role like so:
   - {
        role: user_management
        become: true     # this can be omitted if the play "becomes: true" anyway
     }

The role's defaults defines service_users dictionary:
    * service user accounts
    * on which hosts to create the users
    * distribution of user ssh private and public keys
      SSH keys are taken from Ansible vault.
    * sudo permissions for the user (if the user needs any)
      sudo permissions are installed via an per-user Ansible template.


