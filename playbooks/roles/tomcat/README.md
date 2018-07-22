Sets up a tomcat from a tar archive on the repo server.
It is not a vanilla Tomcat, but a Tomcat tailored towards the Portal.

The SystemV init script `templates/tomcat.init.j2` is not used in our systemd based OS.
It only here for reference or backwards compatibility with manual installtions in FRA or BOS datacenters.
