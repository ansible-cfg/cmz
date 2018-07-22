Provision the Apache/mod_proxy based loadbalancing reverse proxy which distributes requests to subsequent VMs.

Beware that the VM name for our loadbalancing reverse proxy is misleading:
They are referred to as "Web Servers". But they are not. They are loadbalancing reverse proxies.

Starting from the OS Apache package, the only configuration needed is the mod_proxy config.

Background Info on load balancing:
Requesting the Portal through
http://ro1-por-p.ycommerce.ycs.io/
works like so:
- ro1-por-p.ycommerce.ycs.io resolves to the Infrastructure's Edge NSX loadbalancer ro1-cmz-webpvip-001 (10.248.46.240)
- ro1-cmz-webpvip-001 round-robins the request to ro1-cmz-webp-00*.ycommerce.ycs.io
It also terminates the SSL/TLS connection.
- ro1-cmz-webp-00*.ycommerce.ycs.io round-robin the requests to ro1-cmz-porp-00*.ycommerce.ycs.io
(taking care about session stickyness)

There is one exception to this rule: Rundeck.
Rundeck traffic is directly routed from the Infrastructure's Edge NSX loadbalancer to the Rundeck VMs.
Rundeck traffic does not pass our loadbalancing reverse proxy.
Nor is SSL traffic terminated at the Edge NSX loadbalancer, instead SSL traffic is just forwarded to the Rundeck servers.
