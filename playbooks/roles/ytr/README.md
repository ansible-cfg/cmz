ytestrunner2
============

The Ansible role to install a yTestRunner2 server.


Before you use this role
------------------------

The host(s) that you run this role on must be RedHat or CentOS.  You will need to become root when using this role.


Role Variables
--------------

See defaults/main.yml, they are named descriptively

Dependencies
------------

* java - Installs a JDK
* selenium - Installs Selenium and Firefox


Deployment using Ansible:
-------------------------

## Deployment

yTR2 versions are available through Hybris' Artifactory.

`mgmtzone_automation/playbooks/roles/ytr/tasks/deployment*.yml` is the code which does the deployment.

The URLs of artefacts to deploy should be passed into the play.
Otherwise defaults defined in group_vars/ and roles/ytr/defaults/main.yml apply.
Here is an example for a Ro1 Dev depoyment:
```
# VPN into Ro1

# ssh into the Ro1 Dev Control VM and become svc_ro1ansible:
c5258432@ycs.io@ro1-cmz-ctrls-001$  sudo -u svc_ro1ansible -i

# change into the Ansible base directory and get the latest code from git branch master:
cd git_hcs-pdo-sre/mgmtzone_automation
git checkout master
git pull

# Deploy the latest yTR2 SNAPSHOT and run yTR2 checks:
ansible-playbook playbooks/ytr.yml \
--tags deploy_ytr2,test_ytr2  --skip-tags shared \
--extra-vars 'ytestrunner2_core_url=https://repository.hybris.com/hcs-snapshot/com/hybris/cs/pqe/ytestrunner2/develop-SNAPSHOT/ytestrunner2-develop-SNAPSHOT-boot.jar' \
--extra-vars 'ytestrunner2_hybris_url=https://repository.hybris.com/hcs-snapshot/com/hybris/cs/pqe/ytr2hybris/develop-SNAPSHOT/ytr2hybris-develop-SNAPSHOT.jar' \
--extra-vars 'ytestrunner2_legacy_url=https://repository.hybris.com/hcs-snapshot/com/hybris/cs/pqe/ytr2legacy/develop-SNAPSHOT/ytr2legacy-develop-SNAPSHOT.jar'
```

The `--extra-vars` specify the yTR2 artefact download URLs.
Adapt them as needed to install a specific yTR2 SNAPSHOT or RELEASE, e.g.
`https://repository.hybris.com/hcs-release/com/hybris/cs/pqe/ytestrunner2/1.9.16-RELEASE/ytestrunner2-1.9.16-RELEASE-boot.jar`

Do not forget to update the Wiki which lists installed versions per datacenter:
https://wiki.hybris.com/display/MSPIPS/Cloud+Services+Automation+Platform+-+Version+Matrix+per+Data+Center


Manual Deployment:
------------------

    The current deployment follows this logic(it can be followed in main.yml):

    1. Stop the application (stop_ytr2.yml)
    2. Moves the current installation to ytestrunner2-previous folder for rollback purpose
    3. Delete the application so that we can start from a clean state (remove_current_installation.yml)
    4. Create the ytestrunner2 user & directories for the application (create_ytr2_structure.yml)
    5. Install ytestrunner2. This consists of 3 steps currently: (install_ytr2.yml)
      1. Download the jars to the remote
      2. Download ytestrunner2 to the local machine, extract the propertytemplates folder which contains the config properties
      3. Use ansible template to install the previously extracted configs to the ytr2 node (the configs have vars defined
        which are evaluated when they are copied to the remote with the ansible template module)
    6. Start the ytestrunner2 (start_ytr2.yml) & port check that it's alive
    7. Run some test against ytestrunner2 to see that it's operational (ytrtests.yml)

    All other yml files (fix_report_ownership, remove_incorrect_ytr2) are used to replace old installations in Syd,Mo & Rot,
    after that they should be removed.

    TODO:
    This deployment method is fairly stable, but it's missing some elements.
    1. As this application is running on more than one machine, it's behind a load balancer (LB). When deployment
       starts the node should be removed from the LB, and after the installation succeeds, put it back.
    2. Rollback needs to be implemented. This means that multiple versions are installed to the machine, and the latest is
       accessed via a symlink.
    3. Some additional health checks need to be implemented, like 'curl'-ing a /health endpoint to see that everything is fine.
    4. Currently no customer environment is available locally, but when it's available, an ssh key needs to be put under "keyfiles"
       so that ytr2 can execute tests against those VMs.
    5. Before starting the deployment, it should be verified that we have access to the resources (jars, ssh-keys), otherwise
       the service becomes unavailable. This can be implemented that the jars are copied to a temporary location & moved when
       all the files / configs are downloaded & set, or via rollback (download & symlink it).

    ROLLBACK:
    Currently in-progress for a more elegant implementation, but this works:
    What it does:
    1. Check that a backup (ytestrunner2-previous folder) exists
    2. Move the failed install & log to /opt/ytestrunner2-failed for later checks
    3. Move the ytestrunner2-previous to ytestrunner2
    4. Start back the application & run smoke-tests

    NOTE: BOTH EXTRA-VARS & TAGS MUST BE SPECIFIED AT RUN, OTHERWISE BACKUP WILL BE DELETED
    How-to use:
    ansible-playbook playbooks/ytr.yml --extra-vars ytestrunner2_rollback=true --tags rollback_ytr2

    WHEN NEW ROLLBACK IS IMPLEMENTED:
    - remove rollback_ytr2.yml & rollback_ytr2_check.yml
    - remove tags from main.yml
    - remove ytestrunner2_rollback from defaults


Additional Info
---------------

    yTR testing:
        curl --user 'yTR2User:PW' --insecure 'https://localhost:8443/help'
        curl --user 'yTR2User:PW' --insecure 'https://localhost:8443/joblist'
        PW see 'ytr2config/basicauth.properties'


Example Usage
-------------

A playbook to call this role would need to look something like this:

    ---

    - hosts: ytr_servers
      become: true
      become_user: root
      roles:
      - ytr


License
-------

BSD


Author Information
------------------

CSESRE SRE Team
