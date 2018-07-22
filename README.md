<!-- Markdown syntax: https://daringfireball.net/projects/markdown/syntax
     Markdown previewer: http://markdownlivepreview.com/ -->
This repo holds Ansible plays for Commerce Cloud v1.2 provisioning and deployment.

The plays provide:

- Provisioning some of the management zone server types, e.g. the CMDB server, Portal server, yTR server, etc.

- Deployment of Commerce Cloud v1.2 applications Portal and yTR2 into datacenter management zones.

- Some utility stuff, e.g. testing connectivity in datacenters, installing Ansible

The plays are written for new datacenters (Rot, Sydney, Moscow, ...).
They will not work out-of-the box with the classic datacenters Frankfurt and Boston.

For documentation visit the [SRE Wiki page](https://wiki.hybris.com/display/sre/SRE+Management+Zone+Automation).
