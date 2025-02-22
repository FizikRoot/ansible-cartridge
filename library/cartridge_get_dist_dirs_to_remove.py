#!/usr/bin/env python

import os
import re

from ansible.module_utils.helpers import Helpers as helpers

argument_spec = {
    'app_name': {'required': False, 'type': 'str'},
    'app_install_dir': {'required': True, 'type': 'str'},
    'keep_num_latest_dists': {'required': True, 'type': 'int'},
}


def is_dist(filename, app_install_dir, app_name):
    if not os.path.isdir(os.path.join(app_install_dir, filename)):
        return False

    DIST_DIR_RGX = r'^%s-\d+\.\d+\.\d+-\d+(-\S+)?$' % app_name
    return re.match(DIST_DIR_RGX, filename) is not None


def get_dist_dirs_to_remove(params):
    app_name = params['app_name']
    keep_num_latest_dists = params['keep_num_latest_dists']
    app_install_dir = params['app_install_dir']

    if keep_num_latest_dists <= 0:
        return helpers.ModuleRes(failed=True, msg='"keep_num_latest_dists" should be > 0')

    dists = list(filter(
        lambda filename: is_dist(filename, app_install_dir, app_name),
        os.listdir(app_install_dir)
    ))

    dists = sorted(
        dists,
        key=lambda filename: os.path.getmtime(os.path.join(app_install_dir, filename)),
        reverse=True,
    )

    dists_dirs_to_remove = [
        os.path.join(app_install_dir, filename)
        for filename in dists[keep_num_latest_dists:]
    ]

    return helpers.ModuleRes(fact=dists_dirs_to_remove)


if __name__ == '__main__':
    helpers.execute_module(argument_spec, get_dist_dirs_to_remove)
