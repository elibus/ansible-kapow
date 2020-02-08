#!/usr/bin/python

# Copyright: (c) 2020, Marco Tizzoni <elibus@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': [' preview' ],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: kapow_route

short_description: Configure kapow routes

version_added: "1.0"

description:
    - "Configure kapow routes"

options:
    method:
        description: HTTP method (GET or POST)
        required: false
        default: GET
        choices: [ "GET", "POST" ]
    url_pattern:
        description: kapow url_pattern
        required: true
    command:
        description: kapow script to run
        required: true
    entrypoint:
        description: kapow entrypoint
        required: false
        default: '/bin/sh -c'
    state:
        description: state of the route
        required: false
        default: present
        choices: [ "present", "absent" ]
    control_url:
        description: kapow control url
        required: false
        default: http://localhost:8081
author:
    - Marco Tizzoni (@elibus)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  kapow_route:
    method: get
    route: "/hello"
    command: 'echo hello world | kapow set /response/body'
    state: 'present'
'''

RETURN = '''
id:
    description: route id
    type: str
    returned: success
method:
    description: the HTTP method
    type: str
    returned: success
url_pattern:
    description: the route
    type: str
    returned: success
entrypoint:
    description: entrypoint
    type: str
    returned: success
command:
    description: The command for the route
    type: str
    returned: success
'''

from ansible.module_utils.basic import AnsibleModule

import subprocess
import json

def kapow_get_route(module, method, url_pattern, command, entrypoint, control_url):
    out = subprocess.Popen(
        [ 'kapow', 'route', 'list', 
            '--control-url', str(control_url)
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    stdout,stderr = out.communicate()
    if out.returncode != 0:
        module.fail_json(msg='Failed to list kapow routes. Error: %s' % stderr)
    
    routes = json.loads(stdout)
    for r in routes:
        if (
            r["method"] == method and
            r["url_pattern"] == url_pattern and
            r["command"] == command and
            r['entrypoint'] == entrypoint
        ):
            return r

def kapow_remove_route(module, route, control_url):
    route_id = route['id']
    out = subprocess.Popen(
        [ 'kapow', 'route', 'remove', 
            '--control-url', control_url,
            route_id
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    stdout,stderr = out.communicate()
    if out.returncode != 0:
        module.fail_json(msg='Failed to remove kapow route %s. Error: %s' % (route, stderr))

def kapow_add_route(module, method, url_pattern, command, entrypoint, control_url):
    out = subprocess.Popen(
        [ 'kapow', 'route', 'add', 
            '--control-url', control_url,
            '-X', method,
            '-c', command,
            '-e', entrypoint,
            url_pattern
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    stdout,stderr = out.communicate()
    if out.returncode != 0:
        module.fail_json(msg='Failed to add kapow route. Error: %s' % stderr)
    
    return json.loads(stdout)

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        method=dict(type='str', required=False, default='GET'),
        url_pattern=dict(type='str', required=True),
        command=dict(type='str', required=True),
        entrypoint=dict(type='str', required=False, default='/bin/sh -c'),
        state=dict(type='str', required=False, default='present'),
        control_url=dict(type='str', required=False, default='http://localhost:8081')
    )

    result = dict(
        changed=False,
        route=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    method = module.params['method']
    url_pattern = module.params['url_pattern']
    command = module.params['command']
    entrypoint = module.params['entrypoint']
    state = module.params['state']
    control_url = module.params['control_url']

    # Check inputs
    if method not in ['GET', 'POST']:
        module.fail_json(msg='Invalid method: %s' % method)

    if state not in ['present', 'absent']:
        module.fail_json(msg='Invalid state: %s' % state)
    
    # Check if the route exists
    route = kapow_get_route(module, method, url_pattern, command, entrypoint, control_url)

    result['route'] = route
    result['changed'] = False
    
    # Enforce the route state
    if not route and state == 'present':
        result['changed'] = True
        if not module.check_mode:
            result['route'] = kapow_add_route(module, method, url_pattern, command, entrypoint, control_url)

    if route and state == 'absent':
        result['changed'] = True
        if not module.check_mode:
            kapow_remove_route(module, route, control_url)

    # if the user is working with this module in only check mode we do  
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()