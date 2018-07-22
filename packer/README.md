# Packer CentOS build

## Requirements

The following software must be installed/present on your local machine before you can use Packer to build the Vagrant box file:

  - [Packer](http://www.packer.io/)
  - [Vagrant](http://vagrantup.com/)
  - [VirtualBox](https://www.virtualbox.org/) (if you want to build the VirtualBox box)
  - In case of Windows: Git for Bash shell or equivalent

## Usage

Make sure all the required software (listed above) is installed, then cd to the directory containing this README.md file, and run:

    $ ./run_packer.sh

After build has finished:
    $ vagrant box add ./builds/virtualbox-centos7.box --name [[some name]] --provider virtualbox
