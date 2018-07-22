Ansible role to deploy the automationportal, cmdbadaptor or middleware artefacts onto Portal VMs


## Deployment

The Portal consists of many individual components which work together.
Technically spoken every components is a Java application bundled up into a .war or .jar archive.
Every component is versioned and available through Hybris' Artifactory.
So, let's refer to them as artefacts hereafter.

`mgmtzone_automation/playbooks/roles/PortalServer/tasks/deployment*.yml` is the code which does the deployment.

Artefact versions to deploy need to be passed into the play, or the play fails.
Here is an example for a Ro1 Dev depoyment:
```
# VPN into Ro1

# ssh into the Ro1 Dev Control VM and become svc_ro1ansible:
c5258432@ycs.io@ro1-cmz-ctrls-001$  sudo -u svc_ro1ansible -i

# change into the Ansible base directory and get the latest code from git branch master:
cd git_hcs-pdo-sre/mgmtzone_automation
git checkout master
git pull

# deploy the automationportal and run its selfcheck:
ANSIBLE_LOG_PATH=/var/log/ansible/DeployAutomationPortal.log \
ansible-playbook playbooks/DeployAutomationPortal.yml --skip-tags shared \
--extra-vars 'artefact_type=hcs-snapshot' --extra-vars 'automationportal_version=1.19'

# deploy the middleware and run its selfcheck:
ANSIBLE_LOG_PATH=/var/log/ansible/DeployMiddleware.log \
ansible-playbook playbooks/DeployMiddleware.yml --skip-tags shared \
--extra-vars 'artefact_type=hcs-snapshot' --extra-vars 'middleware_version=1.6.2'

# deploy the cmdbadaptor and run its selfcheck:
ANSIBLE_LOG_PATH=/var/log/ansible/DeployCmdbAdaptor.log \
ansible-playbook playbooks/DeployCmdbAdaptor.yml --skip-tags shared \
--extra-vars 'artefact_type=hcs-snapshot' --extra-vars 'cmdbadaptor_version=1.2.1'
```

Do not forget to update the Wiki which lists installed versions per datacenter:
https://wiki.hybris.com/display/MSPIPS/Cloud+Services+Automation+Platform+-+Version+Matrix+per+Data+Center

### Artefacts with datacenter and/or environment specific settings

Some of the artefacts contain settings which are datacenter and/or environment specific.
Within an artefact you find these settings in a file called application.properties.
Settings usually are key-value pairs.

Some values inside `application.properties` are Ansible variables.
It is Ansible's task to replace these variables with the correct values depening on the target datacenter and environment at deployment time.

At deployment time Ansible downloads the artifact from Artifactory to the Ansible control machine.
It extracts the application.properties file to a temporary location.
It treats application.properties as an Ansible template. i.e. it replaces all Ansible variables inside application.properties with matching variables which are in the scope of the current Ansible play.

The variables and their values which are in the current scope are defined in the `playbooks/group_vars/` directory.
Making use of Ansible's variable overwriting capabilities using the `group_vars/` mechanism.

#### Here is an example:
The artefact `middleware.war` contains an `application.properties` file which contains:
```
modules_cmdb_endPoint: {{portal_modules_cmdb_endPoint}}
```
Ansible needs to replace the variable `{{portal_modules_cmdb_endPoint}}` with an actual value.
That value must be the correct value for the datacenter and environment the Ansible play is currently running against.

Let's pretend the Ansible play is run against the Moscow datacenter and its production environment.
Ansible would find the variable called `portal_modules_cmdb_endPoint` in `group_vars/Mo2Prd/middleware.yml`
The value might be: `http://mo2-por-p.ycommerce.ycs.io:8080/cmdb-adaptor`
Ansible would substitute the variable inside the `application.properties` template with the value above.
And write the template to an `application.properties` file on the Portal VM in Moscow containing:
`modules_cmdb_endPoint: "http://mo2-por-p.ycommerce.ycs.io:8080/cmdb-adaptor"`


#### Maintaining datacenter/environment specific variables

This is a joint-venture between the Portal developers and SRE.
The portal devs know which variables need datacenter/environment localization.
They put the variable into application.properties and distriubte application.properties via Artifactory.
They tell us the variable name and wheter it is a secret variable not to be submitted to git in plaintext.

We add the variable to our `group_vars/`
In our example to `group_vars/Mo2Prd/middleware.yml`
Or, if it were a secret variable to `group_vars/Mo2Prd/middleware.vault.yml`



## Overwriting a manually installed Portal version

If you need to run the portal playbook on a VM with a manually
installed Portal version, run the following commands first:
```
systemctl stop tomcat  && \
rm -rf /opt/automation /opt/apache-tomcat-8.5.12 /opt/tomcat
```
/opt/apache-tomcat-8.5.12 might be a different tomcat version.
/opt/tomcat links to /opt/apache-tomcat-VERSION
