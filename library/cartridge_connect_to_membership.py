#!/usr/bin/env python

from ansible.module_utils.helpers import Helpers as helpers

argument_spec = {
    'console_sock': {'required': True, 'type': 'str'},
    'module_hostvars': {'required': True, 'type': 'dict'},
    'play_hosts': {'required': True, 'type': 'list'},
}


def probe_server(control_console, uri):
    return control_console.eval_res_err('''
        local advertise_uri = ...
        if require('membership').get_member(advertise_uri) ~= nil then
            return false
        end
        return require('cartridge').admin_probe_server(advertise_uri)
    ''', uri)


def connect_to_membership(params):
    control_console = helpers.get_control_console(params['console_sock'])
    module_hostvars = params['module_hostvars']
    play_hosts = params['play_hosts']

    changed = False

    instances_to_probe = {
        instance_name: instance_vars
        for instance_name, instance_vars in module_hostvars.items()
        if all([
            not helpers.is_stateboard(instance_vars),
            helpers.not_disabled(instance_vars),
            'config' in instance_vars,
        ])
    }

    for instance_name, instance_vars in instances_to_probe.items():
        connected, err = probe_server(control_console, instance_vars['config']['advertise_uri'])
        if err is not None and instance_name in play_hosts:
            return helpers.ModuleRes(failed=True, msg=err)

        if connected:
            changed = True

    return helpers.ModuleRes(changed=changed)


if __name__ == '__main__':
    helpers.execute_module(argument_spec, connect_to_membership)
