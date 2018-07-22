Role Name
=========

Role to install Java.

Role Variables
--------------

* repo_server
  The DNS name or IP address of the repository server where the RPM will be downloaded from.
* java_vendor
  The vendor of the Java vendor to use. Valid values are SAP and Oracle. The default is Oracle.
* java_version  
  The specific version you want to install. The default depends on the vendor and is 1.8.0_144 for Oracle
  and 8.1.032 for SAP. Note that if you want to overwrite this you have to use the format which is used in
  the RPM file name.

Example Playbook
----------------

    - hosts: whoever-needs-java
      roles:
         - role: java

License
-------

Proprietary

Author Information
------------------

Dennis Benzinger (D061345) <dennis.benzinger@sap.com>
