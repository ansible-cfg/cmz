Role for Installing MySQL 5.5.57 on RedHat Enterprise Linux

Keep this role generic!
Rather than adding resources/configuration for your specific usecase,
include the generic MySQL role in your Ansible playbook and add your specific resources there.

Due to political reasons MySQL is not part of the OS package repostiroy.
We need to install it from a MySQL "bundle" taken from the repo servers.
The repo servers get the bundle from mysql.com via manual upload.
See comments in `tasks\mysql_packages.yml` for details.

Special care has to be taken if MariaDB libraries are already installed on the system.
Again, see comments in `tasks\mysql_packages.yml` for details.


# Variables:

install_server: True    Install MySQL server- and client-resources.
install_server: False   Only install MySQL client resources.

