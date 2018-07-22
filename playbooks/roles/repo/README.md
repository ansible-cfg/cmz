Provision the Repo(sitory) server.
It serves all kinds of binary resources using Apache.
It also stores the CMDB backups.

By default apache is not installed.
Because as of 11/2017 Rundeck installs the repo server Apache.

We explicitly need to call the apache role using:
`--extra-vars install_apache=True`
until Rundeck does not install the repo server any more.
