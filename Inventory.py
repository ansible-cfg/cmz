#!/usr/bin/python

'''
    This script prints hostlists of our datacenter.
    To be used (not only) by:
    * Ansible as a dynamic inventory
    * the checkConnectivity utility scripts

    At some point in the future we might to merge this Inventory with the Monitoring Inventory:
    https://enterprise-stash.hybris.com/projects/HCS-PDO-MON/repos/project-x/browse/inventory.py
'''

import argparse
import os
import re
import json
import socket


# List of datacenters, vagrant is a local Vagrant based test datacenter
datacenters = ['vagrant', 'ro1', 'sy2', 'mo2', 'ddv', 'ns1', 'dqa', 'stg']

# Mapping between environment names and abbreviation
environments = {
    'd': 'dev',
    's': 'stg',
    'p': 'prd',
    'q': 'qa',
}

# List of all server types and their corresponding Ansible group
# Syntax: Ansible groupname: servertype abbreviation
servertypes = {
    'Control':      'ctrl',
    'Web':          'web',
    'Cmdb':         'cmdb',
    'Rundeck':      'rdk',
    'yTestRunner':  'ytr',
    'Portal':       'por',
    'Repo':         'repo',
}



'''
    Commandline parsing: parse environment + servertype into lists of values
'''

# custom actions for parsing the servertype argument:
class ParseArgumentServertype(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        out = values[0].split(',')
        setattr(namespace, self.dest, out)

desc = '''
Generate lists of VMs of a datacenter's management zone according to hostname.
By default the list of VMs is printed in Ansible dynamic inventory syntax.
The output format can be changed to a whitespace seperated plaintext list using the --text option.
The option --servertype can be used together with the --text option to filter the list by servertype.
'''
parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '--text', '-t',
    action='store_true',
    help='Print a whitespace seperated plaintext list of VMs instead of Ansible inventory syntax.'
)
parser.add_argument(
    '--servertype', '-y',
    type=str,
    nargs=1,
    default=servertypes.values(),
    action=ParseArgumentServertype,
    help='One or any comma-delimited combination of: ' + ', '.join(servertypes.values()) + '. E.g. rdk,por,repo. Do not add whitespace between commas. Defaults to all server types. Filtering by server type only takes effect when --text is specified. '
)
parser.add_argument(
    '--static', '-c',
    action='store_true',
    help='Print a static Ansible inventory.'
)
parser.add_argument(
    '--list', '-l',
    action='store_true',
    help='Ansible-syntaxed list of all Ansible inventory groups and their hosts.'
)
parser.add_argument(
    '--host', '-s',
    type=str,
    help='Ansible host vars for a specific host. Always returns an empty JSON hash.'
)

args = parser.parse_args()


'''
    Get the datacenter & environment from the hostname
'''
def getDCEnv(hostname):
    datacenter = re.split('-', hostname)[0] # First part of hostname is the DC ID
    if datacenter not in datacenters:
        raise ValueError("ERROR: Inventory.py - Datacenter part of hostname must be one of %s"  %  datacenters)
    environment = re.split('-',hostname)[2][-1] # Third part - last character specifies the environment
    if environment not in ['d', 's', 'p', 'q']:
        raise ValueError("ERROR: Inventory.py - Application part of hostname must end with 'd', 's', 'p', 'q'")
    return datacenter, environment


'''
    Provide hostlists per datacenter
    Host data taken from: https://wiki.hybris.com/display/yeasy/Commerce+Management+Zone+%28CMZ%29+Requirements
    Will hopefully come from some VMWare API in the future:
    Mohsen Basirat (Icinga Monitoring) has a dynamic Ansible inventory which feeds from VSphere:
    https://enterprise-stash.hybris.com/projects/HCS-PDO-MON/repos/project-x/browse/inventory.py
'''

def getHosts():
    if datacenter == "ddv":
        return [
            "ddv-cmz-rdkd-001.ycommerce.ycsdev.io",
            "ddv-cmz-rdkd-002.ycommerce.ycsdev.io",
            "ddv-cmz-pord-001.ycommerce.ycsdev.io",
            "ddv-cmz-pord-002.ycommerce.ycsdev.io",
            "ddv-cmz-ytrd-001.ycommerce.ycsdev.io",
            "ddv-cmz-ytrd-002.ycommerce.ycsdev.io",
            "ddv-cmz-ctrld-001.ycommerce.ycsdev.io",
            "ddv-cmz-webd-001.ycommerce.ycsdev.io",
            "ddv-cmz-webd-002.ycommerce.ycsdev.io",
            "ddv-cmz-repod-001.ycommerce.ycsdev.io",
            "ddv-cmz-repod-002.ycommerce.ycsdev.io",
            "ddv-cmz-rdkdbd-001.ycommerce.ycsdev.io",
            "ddv-cmz-cmdbd-001.ycommerce.ycsdev.io",
        ]
    if datacenter == "dqa":
        return [
            "dqa-cmz-rdkq-001.ycommerce.ycsdev.io",
            "dqa-cmz-rdkq-002.ycommerce.ycsdev.io",
            "dqa-cmz-porq-001.ycommerce.ycsdev.io",
            "dqa-cmz-porq-002.ycommerce.ycsdev.io",
            "dqa-cmz-ytrq-001.ycommerce.ycsdev.io",
            "dqa-cmz-ytrq-002.ycommerce.ycsdev.io",
            "dqa-cmz-ctrlq-001.ycommerce.ycsdev.io",
            "dqa-cmz-webq-001.ycommerce.ycsdev.io",
            "dqa-cmz-webq-002.ycommerce.ycsdev.io",
            "dqa-cmz-repoq-001.ycommerce.ycsdev.io",
            "dqa-cmz-repoq-002.ycommerce.ycsdev.io",
            "dqa-cmz-rdkdbq-001.ycommerce.ycsdev.io",
            "dqa-cmz-cmdbq-001.ycommerce.ycsdev.io",
        ]

    if datacenter == "stg":
        return [
            "stg-cmz-rdks-001.ycommerce.ycsdev.io",
            "stg-cmz-rdks-002.ycommerce.ycsdev.io",
            "stg-cmz-pors-001.ycommerce.ycsdev.io",
            "stg-cmz-pors-002.ycommerce.ycsdev.io",
            "stg-cmz-ytrs-001.ycommerce.ycsdev.io",
            "stg-cmz-ytrs-002.ycommerce.ycsdev.io",
            "stg-cmz-ctrls-001.ycommerce.ycsdev.io",
            "stg-cmz-webs-001.ycommerce.ycsdev.io",
            "stg-cmz-webs-002.ycommerce.ycsdev.io",
            "stg-cmz-repos-001.ycommerce.ycsdev.io",
            "stg-cmz-repos-002.ycommerce.ycsdev.io",
            "stg-cmz-rdkdbs-001.ycommerce.ycsdev.io",
            "stg-cmz-cmdbs-001.ycommerce.ycsdev.io",
        ]

    if datacenter == "sy2":
        return [
            "sy2-cmz-rdkp-001.ycommerce.ycs.io",
            "sy2-cmz-rdkp-002.ycommerce.ycs.io",
            "sy2-cmz-porp-001.ycommerce.ycs.io",
            "sy2-cmz-porp-002.ycommerce.ycs.io",
            "sy2-cmz-ytrp-001.ycommerce.ycs.io",
            "sy2-cmz-ytrp-002.ycommerce.ycs.io",
            "sy2-cmz-ctrlp-001.ycommerce.ycs.io",
            "sy2-cmz-webp-001.ycommerce.ycs.io",
            "sy2-cmz-webp-002.ycommerce.ycs.io",
            "sy2-cmz-repop-001.ycommerce.ycs.io",
            "sy2-cmz-repop-002.ycommerce.ycs.io",
            "sy2-cmz-rdkdbp-001.ycommerce.ycs.io",
            "sy2-cmz-cmdbp-001.ycommerce.ycs.io",
        ]

    if datacenter == "ns1":
        return [
            "ns1-cmz-rdkp-001.ycommerce.ycs.io",
            "ns1-cmz-rdkp-002.ycommerce.ycs.io",
            "ns1-cmz-porp-001.ycommerce.ycs.io",
            "ns1-cmz-porp-002.ycommerce.ycs.io",
            "ns1-cmz-ytrp-001.ycommerce.ycs.io",
            "ns1-cmz-ytrp-002.ycommerce.ycs.io",
            "ns1-cmz-ctrlp-001.ycommerce.ycs.io",
            "ns1-cmz-webp-001.ycommerce.ycs.io",
            "ns1-cmz-webp-002.ycommerce.ycs.io",
            "ns1-cmz-repop-001.ycommerce.ycs.io",
            "ns1-cmz-repop-002.ycommerce.ycs.io",
            "ns1-cmz-rdkdbp-001.ycommerce.ycs.io",
            "ns1-cmz-cmdbp-001.ycommerce.ycs.io",
        ]

    if datacenter == "ro1":
        return [
            "ro1-cmz-rdkd-001.ycommerce.ycs.io",
            "ro1-cmz-rdkp-001.ycommerce.ycs.io",
            "ro1-cmz-rdkp-002.ycommerce.ycs.io",
            "ro1-cmz-rdks-001.ycommerce.ycs.io",
            "ro1-cmz-rdks-002.ycommerce.ycs.io",
            "ro1-cmz-pord-001.ycommerce.ycs.io",
            "ro1-cmz-pors-001.ycommerce.ycs.io",
            "ro1-cmz-pors-002.ycommerce.ycs.io",
            "ro1-cmz-porp-001.ycommerce.ycs.io",
            "ro1-cmz-porp-002.ycommerce.ycs.io",
            "ro1-cmz-ytrd-001.ycommerce.ycs.io",
            "ro1-cmz-ytrs-001.ycommerce.ycs.io",
            "ro1-cmz-ytrs-002.ycommerce.ycs.io",
            "ro1-cmz-ytrp-001.ycommerce.ycs.io",
            "ro1-cmz-ytrp-002.ycommerce.ycs.io",
            "ro1-cmz-ctrld-001.ycommerce.ycs.io",
            "ro1-cmz-ctrls-001.ycommerce.ycs.io",
            "ro1-cmz-ctrlp-001.ycommerce.ycs.io",
            "ro1-cmz-webd-001.ycommerce.ycs.io",
            "ro1-cmz-webs-001.ycommerce.ycs.io",
            "ro1-cmz-webs-002.ycommerce.ycs.io",
            "ro1-cmz-webp-001.ycommerce.ycs.io",
            "ro1-cmz-webp-002.ycommerce.ycs.io",
            "ro1-cmz-repod-001.ycommerce.ycs.io",
            "ro1-cmz-repos-001.ycommerce.ycs.io",
            "ro1-cmz-repos-002.ycommerce.ycs.io",
            "ro1-cmz-repop-001.ycommerce.ycs.io",
            "ro1-cmz-repop-002.ycommerce.ycs.io",
            "ro1-cmz-rdkdbd-001.ycommerce.ycs.io",
            "ro1-cmz-rdkdbs-001.ycommerce.ycs.io",
            "ro1-cmz-rdkdbp-001.ycommerce.ycs.io",
            "ro1-cmz-cmdbs-001.ycommerce.ycs.io",
            "ro1-cmz-cmdbd-001.ycommerce.ycs.io",
            "ro1-cmz-cmdbp-001.ycommerce.ycs.io",
        ]

    if datacenter == "mo2":
        return [
            "mo2-cmz-rdkp-001.ycommerce.ycs.io",
            "mo2-cmz-rdkp-002.ycommerce.ycs.io",
            "mo2-cmz-porp-001.ycommerce.ycs.io",
            "mo2-cmz-porp-002.ycommerce.ycs.io",
            "mo2-cmz-ytrp-001.ycommerce.ycs.io",
            "mo2-cmz-ytrp-002.ycommerce.ycs.io",
            "mo2-cmz-ctrlp-001.ycommerce.ycs.io",
            "mo2-cmz-webp-001.ycommerce.ycs.io",
            "mo2-cmz-webp-002.ycommerce.ycs.io",
            "mo2-cmz-repop-001.ycommerce.ycs.io",
            "mo2-cmz-repop-002.ycommerce.ycs.io",
            "mo2-cmz-rdkdbp-001.ycommerce.ycs.io",
            "mo2-cmz-cmdbp-001.ycommerce.ycs.io",
        ]

    if datacenter == "vagrant":
        return [
            "vagrant-cmz-ctrlp-001.local",
            "vagrant-cmz-webp-001.local",
            "vagrant-cmz-cmdbp-001.local",
            "vagrant-cmz-rdkp-001.local",
            "vagrant-cmz-ytrp-001.local",
            "vagrant-cmz-ytrp-002.local",
            "vagrant-cmz-porp-001.local",
            "vagrant-cmz-porp-002.local",
            "vagrant-cmz-repop-001.local",
        ]



'''
   Function for filtering hostnames based on a regular expression
'''

def filterHosts(pattern):
    ###print 'regexp filter pattern = %s'  %  pattern
    filter = re.compile(pattern)

    out = []

    for hostname in getHosts():
        match = re.search(filter, hostname)
        if match:
            out.append(hostname)

    return out



'''
    Build an Ansible inventory
    Ansible dynamic inventory syntax see: http://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html
'''

def buildAnsibleInventory():
    inv = {}
    for groupname, stype in servertypes.iteritems():
        inv[groupname] = filterHosts('%s-cmz-%s%s-\d+'  %  (datacenter, stype, environment))

    # Inventory groups for group_vars variable inheritance:
    inv[datacenter.title() + environments[environment].title()] = {}
    inv[datacenter.title() + environments[environment].title()]['children'] = servertypes.keys()

    inv[datacenter.title()] = {}
    inv[datacenter.title()]['children'] = servertypes.keys()

    inv['all'] = {
        'hosts': filterHosts('%s-cmz-[a-z]+?%s-\d+'  %  (datacenter, environment)),
        'vars': {}
    }

    # hostvars for individual hosts:
    inv['_meta'] = {
        'hostvars': {}
    }

    return inv



'''
    print various lists of VMs depending on user input and environment
'''

if args.text is True:
    print " ".join(filterHosts('%s-cmz-(%s)%s-\d+'  %  (datacenter, '|'.join(args.servertype), environment)))
    exit()

if args.host:
    print '{}'
    exit()

datacenter, environment = getDCEnv(socket.gethostname())
inventory = buildAnsibleInventory()

if args.static is True:
    for group, hosts in inventory.iteritems():
        if group == "_meta" or group == "all":
            continue
        if type(hosts) is dict:
            print '[%s:children]'  %  group
            for host in inventory[group]['children']:
                print host
        else:
            print '[%s]'  %  group
            for host in hosts:
                print host
        print
    exit()

if args.list is True:
    print(json.dumps(inventory, sort_keys=True, indent=2))
    exit()

print(json.dumps(inventory, sort_keys=True, indent=2))
