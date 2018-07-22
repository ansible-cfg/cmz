[`Vagrantfile`](Vagrantfile) to start test environment

This [`Vagrantfile`](Vagrantfile) is written so that it uses [`vagrant-cmz.yml`](vagrant-cmz.yml) file, which contains the VM information. This abstracts away Vagrant ruby code, so that only the VM configurations needs to be specified. The VM's are configured via static IP addresses, `/etc/hosts` of all VM's are populated with all available hosts during `vagrant provision`.

Ports are forwarded for most applications where applicable, taking the 
last octet + adding ports (mostly, check the yml for confirmation).
Two notable exceptions is the mysql which is mapped to port 30000,
and the web loadbalancer which is mapped to port 8080 + 8443.

The following options can be set via the YAML config:
```yml
defaults:                    # Default configuration for all VM's
  box: "csesre/centos74"     # The box image name that is used
  box_checksum_type: sha256  # Checksum method to be used
  box_checksum: "b99e62..."  # Checksum of the box. If mismatched, Vagrant will fail to start the VM
  cpu: 1                     # Number of CPUs
  memory: 512                # Size of memory in MB

server_list:                 # This is where the specific VM's are defined
  - name: ctrl_001           # Name of the VM that shows up in Vagrant
    hostname: v-ctrld-001..  # The hostname of the VM
    ipaddr: "1.2.3.4"        # IP address of the VM

    file:                    # File provider is used when specifying files via this
      - ssh_key:
        src: "./VagrantInsecurePrivateKey"
        dest: "/home/vagrant/.ssh/id_rsa"
      - ssh_key2:
        src: "./VagrantInsecurePrivateKey"
        dest: "/home/vagrant/.ssh/id_rsa2"

    shell:                   # Shell provider is used when specifying files
      - "../utils/ssh_permissions.sh"
      - "../utils/installAnsible.sh"

    synced_folder:           # Mount a synced folder
        src: "../.."
        dest: "/home/vagrant/git_hcs-pdo-sre"
    
    portforward:
      - service_name:
        guest: 80
        host: 8080
```
For a working full file, see [`vagrant-cmz.yml`](vagrant-cmz.yml).
