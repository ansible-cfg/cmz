Ansible play to provision Portal VMs

## Portal middleware Ansible plays:

The Portal servers have its own installation of Ansible in a Python virtual environment.
The Portal VM's Ansible installaton is independent of the management zone Ansible installed on the Control VMs.
Tomcat on the Portal VM's executes Ansible plays, aka. Middleware Ansible plays, which are also installed in the Python virtual env.

### Example: the middleware play

The play gets the list of remote hosts via commandline like so:
```
    ansible-playbook /opt/automation/ansiblemiddleware/ansible/playbooks/apache_maintenance.yml \
    -e '{"activityKey":1156,
         "mode":true,
         "notificationUrl":"http://sy2-cmz-porp-001.ycommerce.ycs.io:8080/middleware/notifications/maintenance",
         "hostGroups":[{"type":"web","hosts":["sy2-cust-alpha-d2-web-001"]}]
    }'
```
If the remote host is in the customer zone:

1. new DCs:
    Tomcat has the svc_sy2portal2ssh service user's private key in ~/.ssh/id_rsa-svc_sy2portal2ssh:
    ```
        [root@sy2-cmz-porp-001 ~]# locate '*id_rsa*'
            /home/svc_sy2portal2ssh/.ssh/id_rsa
            /home/tomcat/.ssh/id_rsa-svc_sy2portal2ssh
            /opt/automation/master-config/middleware/id_rsa
        [root@sy2-cmz-porp-001 automation]# locate '*id_rsa*' | xargs -i'{}' ssh-keygen -l -f {}
            4096 SHA256:NiISHdHgzNNESN2x+cxzLkdNs6N0b2SjKb6y/c+8U1c svc_sy2portal2ssh@sy2-cmz-ljp-001.ycommerce.ycs.io (RSA)
            4096 SHA256:NiISHdHgzNNESN2x+cxzLkdNs6N0b2SjKb6y/c+8U1c svc_sy2portal2ssh@sy2-cmz-ljp-001.ycommerce.ycs.io (RSA)
            4096 SHA256:NiISHdHgzNNESN2x+cxzLkdNs6N0b2SjKb6y/c+8U1c no comment (RSA)
            4096 SHA256:NiISHdHgzNNESN2x+cxzLkdNs6N0b2SjKb6y/c+8U1c no comment (RSA)
        Middleware Java uses:
            /opt/automation/webapps/middleware/middleware-1.3.3/WEB-INF/classes/application-prod.properties,
            /opt/automation/master-config/middleware/application-prod.properties:
                middleware.ssh.key=/opt/automation/master-config/middleware/id_rsa

    /home/tomcat/.ssh/config instructs Tomcat to connect to any sy2-* host as the user svc_sy2portal2ssh:

        [root@sy2-cmz-porp-001 ~]# cat /home/tomcat/.ssh/config
            Host sy2-*
              StrictHostKeyChecking no
              UserKnownHostsFile /dev/null
              User svc_sy2portal2ssh
              IdentityFile ~/.ssh/id_rsa-svc_sy2portal2ssh

    svc_sy2portal2ssh may connect into the customer zone:

        [tomcat@sy2-cmz-porp-001 ~]$ ssh svc_sy2portal2ssh@sy2-e2e-b2b-p1-adm-001.ycommerce.ycs.io
            Creating home directory for svc_sy2portal2ssh.
            Idle users will be removed after 15 minutes

        [svc_sy2portal2ssh@sy2-e2e-b2b-p1-adm-001 ~]$ hostname -f
            sy2-e2e-b2b-p1-adm-001.ycommerce.ycs.io
    ```
2. classic DCs (not verified!):
    Tomcat can access the Rundeck service user's private key
    /home/tomcat/.ssh/config instructs Tomcat to connect to any *-fr-* host as the user srvc_JeDNUd
    and to connect via the Management Zone Rundeck box as a jumphost
