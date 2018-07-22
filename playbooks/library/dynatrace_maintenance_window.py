#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'SAP'
}

DOCUMENTATION = '''
---
module: dynatrace_maintenance_window

short_description: This is my dynatrace_maintenance_window module

version_added: "2.3"

description:
    - "This is my longer description explaining my dynatrace_maintenance_window module"

options:
    api_url:
        description:
            - The Dynatrace API endpoint starting with 'https://' and ending with '/api/v1/'
        required: true
    api_token:
        description:
            - The Dynatrace API token which should be used.  This value will not be printed onin logs.
        required: true
    validate_certs:
        description:
            - This is the generic Ansible parameter for web requests and will allow working with insecure server certificates, default: true
        required: false
    timeout_seconds:
        description:
            - This is the generic Ansible parameter 'timeout' for web requests, default: 30
        required: false
    command:
        description:
            - What is the requested operation, can be 'list', 'set', or 'delete'
        required: true
    id:
        description:
            - Required to specify for 'set' and 'delete' operations: which maintenance window should be changed
        required: false
    type:
        description:
            - Only for 'set' operation: is the maintenance window 'Planned' or 'Unplanned', default: 'Planned'
        required: false
    description:
        description:
            - Optional for 'set' operation: if any text should be added to the maintenance window
        required: false
    suppress_alerts:
        description:
            - Only for 'set' operation: stop the alerts during the maintenance window or not, default: True
        required: false
    suppress_problems:
        description:
            - Only for 'set' operation: stop flagging problems during the maintenance window or not, default: True
        required: false
    tags:
        description:
            - Only for 'set' operation: which host tags are included in the maintenance window, default: empty list
        required: false
    begin_time:
        description:
            - Only for 'set' operation: when the maintenance window start, format is 'YYYY-MM-DD HH:MM' where HH is 00-23
        required: false
    end_time:
        description:
            - Only for 'set' operation: when the maintenance window ends, format is 'YYYY-MM-DD HH:MM' where HH is 00-23
        required: false
    timezone:
        description:
            - Only for 'set' operation: timezone of the 'begin_time' and 'end_time' values
        required: false

extends_documentation_fragment: []

author:
    - SAP
'''

EXAMPLES = '''
# List all maintenance windows
- name: get all maintenance windows from Dynatrace
  dynatrace_maintenance_window:
    api_url: "https://.../api/v1/"
    api_token: "xxxxxx"
    command: list
  register: api_result
- debug:
    var: api_result.response_json

# Create or change a specific maintenance window
- name: set a maintenance window in Dynatrace
  dynatrace_maintenance_window:
    api_url: "https://.../api/v1/"
    api_token: "xxxxxx"
    command: set
    id: "test1"
    description: "This is just a test"
    tags: [ "CMZ", "[Environment]env:staging", "[Environment]role:ytr" ]
    begin_time: "2018-05-12 00:00"
    end_time: "2018-05-13 00:00"
    timezone: "Europe/Budapest"

# fail the module
- name: delete a maintenance window from Dynatrace
  dynatrace_maintenance_window:
    api_url: "https://.../api/v1/"
    api_token: "xxxxxx"
    command: delete
    id: "test1"
'''

RETURN = '''
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, url_argument_spec

def ensure_param_exists(module, param_name):
    if not module.params[param_name]:
        module.fail_json(msg='Parameter %s is not specified or empty' % param_name, response=None, changed=False)

def run_module():
    maintenance_window_spec=dict(
        id                 =dict(type='str'),
        type               =dict(type='str', choices=['Planned', 'Unplanned'], default='Planned'),
        description        =dict(type='str'),
        suppress_alerts    =dict(type='bool', default=True),
        suppress_problems  =dict(type='bool', default=True),
        tags               =dict(type='list', default=[]),
        begin_time         =dict(type='str'),
        end_time           =dict(type='str'),
        timezone           =dict(type='str'),
    )

    argument_spec = maintenance_window_spec.copy()
    argument_spec.update(dict(
        api_url           =dict(type='str', required=True),
        api_token         =dict(type='str', required=True, no_log=True),
        validate_certs    =dict(type='bool', default=True),
        timeout_seconds   =dict(type='int', default=30),
        command           =dict(type='str', required=True, choices=['list', 'set', 'delete']),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # validate the parameters
    api_url = module.params['api_url']
    if not api_url.startswith('https://'):
        module.fail_json(msg='api_url should start with https://', response=None, changed=False)
    if not api_url.endswith('/'):
        api_url += '/'
    if not api_url.endswith('/api/v1/'):
        module.fail_json(msg='api_url should end with /api/v1/', response=None, changed=False)
    api_url += 'maintenance'

    command = module.params['command']
    if command == 'set':
        ensure_param_exists(module, 'id')
        ensure_param_exists(module, 'tags')
        ensure_param_exists(module, 'begin_time')
        ensure_param_exists(module, 'end_time')
        ensure_param_exists(module, 'timezone')
    elif command == 'delete':
        ensure_param_exists(module, 'id')

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        if command in {'set', 'delete'}:
            return dict(changed=False)
        else:
            return dict(changed=False, status={})


    http_headers = {'Authorization': 'Api-Token ' + module.params['api_token']}
    if command == 'list':
        response_body, response = fetch_url(module, url=api_url, method='GET', headers=http_headers,
                                            timeout=module.params['timeout_seconds'])

        status_code = response["status"]
        if status_code != 200:
            module.fail_json(msg='Unexpected API response', response_json=[], response=response, changed=False)

        response_json = json.load(response_body)
        module.exit_json(response_json=response_json, response=response, changed=False)

    elif command == 'set':
        # prepare the request as json object as Dynatrace API expects
        json_tags = []
        for tag_name in module.params['tags']:
            tag_value = None
            if ':' in tag_name:
                (tag_name, tag_value) = tag_name.split(':')
                json_tags.append({ 'context': 'CONTEXTLESS', 'key': tag_name, 'value': tag_value})
            else:
                json_tags.append({ 'context': 'CONTEXTLESS', 'key': tag_name})

        json_body = {
            'id': module.params['id'],
            'type': module.params['type'],
            'description': module.params['description'],
            'suppressAlerts': module.params['suppress_alerts'],
            'suppressProblems': module.params['suppress_problems'],
            'scope': {
                'matches': [
                    {
                        'type': 'HOST',
                        'tags': json_tags
                    }
                ]
            },
            'schedule': {
                'type': 'Once',
                'timezoneId': module.params['timezone'],
                'maintenanceStart': module.params['begin_time'],
                'maintenanceEnd': module.params['end_time']
            }
        }

        # remove optional keys, if empty
        if not json_body['description']:
            del json_body['description']

        http_headers['Content-Type'] = 'application/json;charset=utf-8'
        response_body, response = fetch_url(module, url=api_url, method='POST', headers=http_headers,
                                            timeout=module.params['timeout_seconds'],
                                            data=json.dumps(json_body))

        if response["status"] != 204:
            module.fail_json(msg='Unexpected API response', response=response, changed=False)

        module.exit_json(response=response, changed=True)

    elif command == 'delete':
        url = api_url + '/' + module.params['id']
        response_body, response = fetch_url(module, url=url, method='DELETE', headers=http_headers,
                                            timeout=module.params['timeout_seconds'])

        status_code = response["status"]
        if status_code != 204:
            module.fail_json(msg='Unexpected API response', response=response, changed=False)

        module.exit_json(response=response, changed=True)

def main():
    run_module()

if __name__ == '__main__':
    main()
