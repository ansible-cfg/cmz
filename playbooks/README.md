To update CMDB/Portal/yTR/... servers use the corresponding playbook (CmdbServer.yml, PortalServer.yml, etc.)

To update all use CMZ.yml. Installing new DCs can be done by setting _load\_initial\_cmdb\_data_ to true in the command line with:

    -e "load_initial_cmdb_data=true"
