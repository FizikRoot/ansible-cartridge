#!/usr/bin/env python

from ansible.module_utils.helpers import Helpers as helpers

argument_spec = {
    'module_hostvars': {'required': True, 'type': 'dict'},
    'play_hosts': {'required': True, 'type': 'list'},
}


def count_disabled_instances(params):
    module_hostvars = params['module_hostvars']
    play_hosts = params['play_hosts']

    rating = {}

    not_started_count = 0
    config_mismatch_count = 0
    started_count = 0

    for instance_name in play_hosts:
        instance_vars = module_hostvars[instance_name]
        disabled_instances = instance_vars['instance_info']['cluster_disabled_instances']
        if disabled_instances == helpers.DisabledInstancesCodes.STATEBOARD:
            continue
        elif disabled_instances == helpers.DisabledInstancesCodes.NOT_STARTED:
            not_started_count += 1
        elif disabled_instances == helpers.DisabledInstancesCodes.CONFIG_MISMATCH:
            config_mismatch_count += 1
        elif type(disabled_instances) == list:
            started_count += 1
            for disabled_instance in disabled_instances:
                rating[disabled_instance] = rating.get(disabled_instance, 0) + 1
        else:
            return helpers.ModuleRes(
                failed=True,
                msg='Unknown type of cluster_disabled_instances value: %s' % disabled_instances,
            )

    if started_count == 0 and config_mismatch_count > 0:
        return helpers.ModuleRes(failed=True, msg='All instances in cluster has different clusterwide configs')

    final_disabled_instances = []
    for name, score in rating.items():
        if score >= started_count / 2:
            final_disabled_instances.append(name)

    return helpers.ModuleRes(changed=False, fact=final_disabled_instances)


if __name__ == '__main__':
    helpers.execute_module(argument_spec, count_disabled_instances)
