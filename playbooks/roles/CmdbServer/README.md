Provision the CMDB VMs.
The CMDB is the persistance layer for the Portal and more.

The CMDB is a MySQL database.
We use a custom MySQL role for installing it.

For loading an initial data set into the CMDB, the `svc_*ansible` service user needs
read access to the `HCS-PDO-CNV/repos/cmdb` repo using ssh protocol and
`svc_*ansible`'s public ssh key.

Loading initial data into the CMDB needs to be done *explicitly*.
Otherwise, we risk overwriting some (production) CMDB unvoluntarily.
If you want to initialize an empty CMDB, please set `load_initial_cmdb_data` to `TRUE`, e.g
by passing `--extra-vars "load_initial_cmdb_data=true"` on the Ansible commandline.

The initial data dump is maintained by the Portal devs.
Please note that it is not idempotent, i.e. loading it will only succeed against an empty CMDB.
