# Multiversion

The default versioning approach for Tarantool Cartridge applications is quite simple:

* only one version of application is installed on a machine;
* updating instance happens on instance restart.

Such approach doesn't protect from accidental updating instance, that can lead to
errors (for example, if router starts to use a new schema earlier than storages).
The solution is using multiversion approach (currently it's fully supported only
for [TGZ](/doc/tgz.md) packages).

Multiversion approach:

* several versions of application can be installed on a machine;
* each instance uses fixed version - it is achieved by using symbolic links;
* updating instance consists of:
  * moving its link to the newest version of application
    (see [`update_instance` step](/doc/scenario.md#update_instance));
  * instance restart.

## Configuration

**To enable multiversion approach `cartridge_multiversion: false` should be set.**

All versions of application are placed in
`{{ cartridge_app_install_dir }}/{{ cartridge_app_name }}-{{ version }}`
directory.

Symbolic links for instances are placed in
`{{ cartridge_app_instances_dir }}/{{ cartridge_app_name }}.{{ instance-name }}`.

For example, we deploy `myapp-1.0.0-0.tgz` and start `instance-1`, `instance-2`
and stateboard.

* Application files are placed in `{{ cartridge_app_install_dir }}/myapp-1.0.0-0`:
  ```bash
  {{ cartridge_app_install_dir }}/myapp-1.0.0-0/
    tarantool
    init.lua
    ...
  ```
* Instances links are placed in `cartridge_app_instances_dir`:
  ```bash
  {{ cartridge_app_instances_dir }}/
    myapp.instance-1 -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
    myapp.instance-2 -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
    myapp-stateboard -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
  ```

## Rotating distributions

Each new version is added to `cartridge_app_install_dir` and sometimes old version
become redundant.
To simply rotate distributions use [`rotate_dists` step](/doc/scenario.md#rotate_dists)

## Example

Let's imagine that we already have `myapp-1.0.0-0` installed:

```bash
{{ cartridge_app_install_dir }}/
  myapp-1.0.0-0/
```

`storage-1`, `storage-2`and `core-1` are using this version of application:

```bash
{{ cartridge_app_instances_dir }}/
  myapp.storage-1 -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
  myapp.storage-2 -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
  myapp.core-1 -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
```

Now the day has come, and we want to deploy next version: `myapp-2.0.0-0.tgz`.
Let's write a playbook that installs a new version and updates storages.

**Note**: it may be useful to specify hosts pattern, e.g. `hosts: *storage*`.

```yaml
- name: Update package
  hosts: all
  vars:
    cartridge_package_path: "./myapp-2.0.0-0.tgz"
    cartridge_scenario:
      - update_package
  roles:
    - tarantool.cartridge

- name: Update storages
  hosts: "*storage*"
  vars:
    cartridge_package_path: "./myapp-2.0.0-0.tgz"
    cartridge_scenario:
      - update_instance
      - restart_instance
  roles:
    - tarantool.cartridge
```

After running this playbook `instance-1` and stateboard use `myapp-2.0.0-0`,
but `instance-2` continue to use `myapp-1.0.0-0`:

```bash
{{ cartridge_app_install_dir }}/
  myapp-1.0.0-0/
  myapp-2.0.0-0/
```

```bash
{{ cartridge_app_instances_dir }}/
  myapp.storage-1 -> {{ cartridge_app_install_dir }}/myapp-2.0.0-0
  myapp.storage-2 -> {{ cartridge_app_install_dir }}/myapp-2.0.0-0
  myapp.core-1 -> {{ cartridge_app_install_dir }}/myapp-1.0.0-0
```

Sometimes we have a lot of distributions in `cartridge_app_install_dir`:

```bash
{{ cartridge_app_install_dir }}/
  myapp-1.0.0-0/
  myapp-2.0.0-0/
  myapp-3.0.0-0/
  myapp-4.0.0-0/
  myapp-5.0.0-0/
```

Let's rotate them:

```yaml
- name: Update storages
  hosts: all
  vars:
    cartridge_keep_num_latest_dists: 2
    cartridge_scenario:
      - rotate_dists
  roles:
    - tarantool.cartridge
```

After running this playbook, there are only 2 last distributions:

```bash
{{ cartridge_app_install_dir }}/
  myapp-4.0.0-0/
  myapp-5.0.0-0/
```
