# Base Image
FROM centos:latest

# Metadata
LABEL base.image="centos:latest"
LABEL software="Ansible"
LABEL software.version="2.3.1.0"
LABEL description="Docker container with Ansible. No default entrypoint is specified, just use it as needed"
LABEL tags="ansible"
# DL SAP Hybris CSS Site Reliability Engineering-Global (External) <DL_59E4C7CBECB2110E030000F7@exchange.sap.corp>
LABEL maintainer="DL_59E4C7CBECB2110E030000F7@exchange.sap.corp"

RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum install ansible-2.3.1.0 unzip python2-pip python-devel gcc -y
RUN pip install shade
