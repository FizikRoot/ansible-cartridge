# Application configuration

There are two ways to change the config:
- [changing the config by section](#config-sections-update)
- [loading the config entirety](#config-uploading)

## Config sections update

[`cartridge_app_config`](/doc/variables.md#cluster-configuration)
variable is used to edit cluster configuration.
It allows defining configuration sections in a special format:

```yaml
cartridge_app_config:
  <section_name>:
    body: <section body>
    deleted: <boolean>
```
**Note:**
* sections with the `deleted` flag set up will be deleted;
* sections not mentioned here won't be changed;
* other sections values will be replaced with the section `body` value.

*Example*

If your cluster configuration looks like:

```yaml
section-1: value-1  # section body is a string

section-2:  # section body is a table
  key-21: value-21
  key-22: value-22

section-3:
  key-31: value-31
```

... after running a role with this `cartridge_app_config`:

```yaml
cartridge_app_config:
  section-2:
    body:
      key-21: value-21-new

  section-3:
    deleted: true
```

... it will be:

```yaml
section-1: value-1  # hasn't been changed

section-2:
  key-21: value-21-new  # body was replaced
```

## Config uploading

[Step `upload_app_config`](/doc/scenario.md#upload_app_config) allows loading
the entire config using Lua API or HTTP endpoint. To do this, you should specify
the path to the configuration file or folder using `cartridge_app_config_path`.

An example of indicating the path to different types of config:

```yaml
cartridge_app_config_path: '../my_app_config.yml'
# OR
cartridge_app_config_path: '../my_app_config.zip'
# OR
cartridge_app_config_path: '../my_app_config_dir'
```

There are 3 modes for config loading:
- `lua` - config will be uploaded by Lua-function `cartridge.config_patch_clusterwide()`;
- `http` - config will be uploaded to `http://localhost:port/admin/config`
  with basic authentication by cluster cookie;
- `tdg` - config will be loaded by a Lua-function in TDG with a version `1.6.15`+ or `1.7.6`+;
  config will be loaded by HTTP in an older version.

To select any of these types, you should use the variable `cartridge_app_config_upload_mode`:
```yaml
cartridge_app_config_upload_mode: 'lua'
# OR
cartridge_app_config_upload_mode: 'http'
# OR
cartridge_app_config_upload_mode: 'tdg'
```

### Upload modes

|              |   Lua mode  |  HTTP mode  | TDG mode |
|--------------|:-----------:|:-----------:|:--------:|
| YAML files   | + (default) |      +      |     -    |
| ZIP files    |      -      | + (default) |     +    |
| Other files  |      -      | + (default) |     +    |
| Folder files |      -      |      -      |     +    |

### Lua mode

To upload file config by Lua, `cartridge.config_patch_clusterwide()` is used.
New config will be parsed, and based on this, the difference will be calculated.
This difference will be used to patch by `cartridge.config_patch_clusterwide()`.

### HTTP mode

If you use HTTP mode to upload a file, then the file will be sent as is
to `http://localhost:port/admin/config`. Also, in this mode will be added
the `Authorization` header for basic authorization using a cluster cookie.

The url used to send the config will be taken from the control instance config
(`http://127.0.0.1:{{ control_instance.http_port }}/admin/config` will be used)
or from the `cartridge_app_config_upload_url` variable. Variable
`cartridge_app_config_upload_url` takes precedence over control instance url.

For example, you can specify the port of the instance,
which is on the same machine as the control instance:
```yaml
cartridge_app_config_upload_url: 'http://10.0.0.102:8083/admin/config'
```

**Note** that directory uploading by HTTP mode is not yet supported.

### TDG mode

> By default, this mode is disabled. To enable it,
> you should select it by `cartridge_app_config_upload_mode` variable:
> ```yaml
> cartridge_app_config_upload_mode: 'tdg'
> ```

TDG mode - smart mode for loading config into TDG.
On new versions of TDG (`1.6.15`+,` 1.7.6`+ or `2.1.0`+),
the ZIP config or directory with the config will be delivered to the machine
and then the path to the config will be transferred to TDG by Lua.
To do this, you do not need to specify an authorization token or HTTP port.

With older versions of TDG, things are a little more complicated.
It's possible to upload config only by HTTP.
Therefore, if authorization is enabled in the application, then it is necessary
to generate a token and pass it to the `cartridge_tdg_token` variable:
```yaml
cartridge_tdg_token: '878e45aa-f79e-4cf9-8938-d5904828c4d2'
```

Also, as with uploading over HTTP, you can select the url of the instance
to which the archive will be uploaded by `cartridge_app_config_upload_url`.

Full example for loading TDG config:
```yaml
cartridge_app_config_path: './tdg_config_dir'
# OR: cartridge_app_config_path: './tdg_config.zip'
cartridge_app_config_upload_mode: 'tdg'
cartridge_tdg_token: '878e45aa-f79e-4cf9-8938-d5904828c4d2'
```
