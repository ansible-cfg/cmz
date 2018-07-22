#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'SAP'
}

DOCUMENTATION = '''
---
module: vra_api

short_description: This is vra_api module

version_added: "2.3"

description:
    - "This vra_api module able to trigger create and revert snapshot operation by vRealize Automation API"

options:
    vra_api_fqdn:
        description:
            - VRA API fully qualified domain name
        required: true
    username:
        description:
            - VRA username
        required: true
    password:
        description:
            - VRA password
        required: true
    validate_certs:
        description:
            - This is the generic Ansible parameter for web requests and will allow working with insecure server certificates, default: true
        required: false
    vmhosts:
        description:
            - One or more target hostnames, as defined in vRA
        required: true
    action:
        description:
            - create_snapshot: option for create a snapshot
            - revert_snapshot: option for revert a snapshot
        required: true

extends_documentation_fragment: []

author:
    - SAP
'''

EXAMPLES = '''
# Create Snapshot
- name: Create Snapshot
  vra_api:
    vra_api_fqdn: ro1-vra.ycs.io
    username: xxxxxx@ycs.io
    password: xxxxxxxxxx
    vmhosts: ro1-cmz-ytrsst-001
    action:  create_snapshot
  register: result
- debug: var=result

# Revert Snapshot
- name: Revert Snapshot
  vra_api:
    vra_api_fqdn: ro1-vra.ycs.io
    user: xxxxxx@ycs.io
    password: xxxxxxxxxx
    vmhosts: ro1-cmz-aaa-001,ro1-cmz-xxx-002
    action:  revert_snapshot
  register: result
- debug: var=result
'''

RETURN = '''
'''

import json, time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

def run_module():
    def api_process(action):

        token_url = "https://" + module.params['vra_api_fqdn'] + "/identity/api/tokens"
        username = module.params['username']
        password = module.params['password']
        tenant = "ycommerce"

        http_headers = {'accept': "application/json", 'content-type': "application/json", }
        payload = '{{"username":"{}","password":"{}","tenant":"{}"}}'.format(username, password, tenant)
        # token id return from vra api
        response_body, response = fetch_url(module, url=token_url, method='POST', data=payload, headers=http_headers, timeout=30)
        response_json = json.load(response_body)

        # generate token id use for api call
        auth = "Bearer " + response_json['id']
        http_token_headers = {'accept': "application/json", 'content-type': "application/json", 'authorization': auth}
        if response["status"] != 200:
            module.fail_json(msg='Unexpected API response for Bearer ID return', response_json=[], response=response, changed=False)

        # loop host if there are multiple hosts
        for host in module.params['vmhosts']:
            # hosts id return
            hostid_url = "https://{}/catalog-service/api/consumer/resources?$filter=name+eq+'{}'".format(
                module.params['vra_api_fqdn'], host)
            response_body, response = fetch_url(module, url=hostid_url, method='GET', headers=http_token_headers)
            response_json = json.load(response_body)
            host_id = response_json['content'][0]['id']
            if response["status"] != 200:
                module.fail_json(msg='Unexpected API response for host ID return', response_json=[], response=response,
                                 changed=False)

            # action of host return
            actions_url = "https://{}/catalog-service/api/consumer/resources/{}/actions/".format(
                module.params['vra_api_fqdn'], host_id)

            response_body, response = fetch_url(module, url=actions_url, method='GET', headers=http_token_headers)
            response_json = json.load(response_body)
            if response["status"] != 200:
                module.fail_json(msg='Unexpected API response for host actions return', response_json=[],
                                 response=response, changed=False)

            dict_actions = {}
            for i in range(0, len(response_json['content']), 1):
                dict_actions[response_json['content'][i]['name']] = response_json['content'][i][
                    'id']  # return {u'Suspend': u'2073db21-f708-44ab-b5b1-f80cf99e7b09', u'Power Off': u'07831a32-0bc7-4f7d-8372-164ea69d61af', u'Connect to Remote Console': u'f6d3a9e1-4c5a-4856-9ced-9f5b491ff93e', u'Delete Snapshot': u'6493a45c-4216-4a03-a866-b1ec0636288a', u'Install Tools': u'7ed95871-d73b-40ba-8c81-7407ef5e4fa1', u'Connect using VMRC': u'b0f8dd39-4f69-47c9-8344-5b2fce37cab5', u'Reboot': u'bab814c5-6b3c-43cf-8ce2-cd04372d526e', u'Change Lease': u'29f5c333-2cc4-4db1-b81e-1fdd46809120', u'Reprovision': u'a19b6255-a6e6-4821-a5a0-bfcb5179bd0e', u'Run Puppet on VM': u'298480d7-b094-4580-a703-e4212429656d', u'Expire': u'a077d4d5-9c2e-45a6-a8c6-2eb42a56de28', u'Shutdown': u'993ae711-88b9-4baa-9678-4cde5694a703', u'Reconfigure': u'649522a2-f9e3-4286-ad51-f35eb73b6548', u'Destroy': u'6f3f00cc-96e7-4c18-92a6-cdf75236b58a', u'Power Cycle': u'b236c593-e0ee-4676-95ed-52ae4b2c2519', u'Revert To Snapshot': u'64936231-171f-4e32-99cb-57e872d892ee'}

            # get actions id from dict_actions
            action_id = dict_actions.get(action)

            if action_id is None:
                pass
            else:
                # get template json(response_json) before post
                template_url = 'https://{}/catalog-service/api/consumer/resources/{}/actions/{}/requests/template'.format(
                    module.params['vra_api_fqdn'], host_id, action_id)
                response_body, response = fetch_url(module, url=template_url, method='GET', headers=http_token_headers)
                response_json = json.load(response_body)
                payload = json.dumps(response_json)

                if response["status"] != 200:
                    module.fail_json(msg='Unexpected API response for template json before post request',
                                     response_json=[], response=response, changed=False)

                # post template json
                post_url = 'https://{}/catalog-service/api/consumer/resources/{}/actions/{}/requests'.format(
                    module.params['vra_api_fqdn'], host_id, action_id)

                response_body, response = fetch_url(module, url=post_url, method='POST', data=payload,
                                                    headers=http_token_headers)

                if response["status"] != 201:
                    module.fail_json(msg='Unexpected API response for requests post', response_json=[],
                                     response=response, changed=False)

                # check process status
                status_url = response['location']
                response_body, response = fetch_url(module, url=status_url, method='get', data=payload,
                                                    headers=http_token_headers)
                if response["status"] != 200:
                    module.fail_json(msg='Unexpected API response for status check', response_json=[],
                                     response=response, changed=False)

                while True:
                    response_body, response = fetch_url(module, url=status_url, method='GET',
                                                        headers=http_token_headers)
                    status = json.load(response_body)['state']
                    print status, "...."
                    time.sleep(5)
                    if status == "SUCCESSFUL":
                        break

    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        vra_api_fqdn  =dict(type='str', required=True),
        username      =dict(type='str', required=True),
        password      =dict(type='str', required=True, no_log=True),
        vmhosts       =dict(type='list', required=True),
        action        =dict(type='str', required=True, choices=['create_snapshot', 'revert_snapshot']),

    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        status=dict(type='list', default=[]),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    if module.params['action'] == 'create_snapshot':
        api_process('Delete Snapshot')
        api_process('Create Snapshot')
        module.exit_json(response=[], changed=True)

    elif module.params['action'] == 'revert_snapshot':
        api_process('Revert To Snapshot')
        api_process('Power On')
        module.exit_json(response=[], changed=True)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()