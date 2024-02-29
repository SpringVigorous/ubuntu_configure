
from dynaconf import Dynaconf
import json

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    # settings_files=['config/settings.toml', 'config/.secrets.toml'],
    settings_files=['config/settings.toml'],
    environments=True,
    # 环境变量前缀，环境变量导出方式 `export CONF_FOO=bar` 变成 `settings.foo == "bar"`
    # envvar_prefix="CONF",
    lowercase_read=True,
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

print(settings.to_dict())

setting_str=json.dumps(settings.to_dict(),
                        indent=4,
                        separators=(",", ":"))

try:
    with open(".settings.json", "w") as f:
        f.write(setting_str)
except IOError as io_err:
    print(f"Error writing to .settings.json: {io_err}")