
from dynaconf import Dynaconf
import json


# dynaconf -i config.settings list

settings = Dynaconf(
    env_switcher="LAUNCH_ENV",
    # envvar_prefix="DYNACONF",

    # settings_files=['config/settings.yaml','config/.secrets.yaml'],
    settings_files=['config/settings.yaml'],
    environments=True,
    # 环境变量前缀，环境变量导出方式 `export CONF_FOO=bar` 变成 `settings.foo == "bar"`
    envvar_prefix="CONFIG",
    lowercase_read=True,
)


settings.setenv("config")


print(settings.to_dict())

setting_str=json.dumps(settings.to_dict(),
                        indent=4,
                        separators=(",", ":"))

try:
    with open(".settings.json", "w") as f:
        f.write(setting_str)
except IOError as io_err:
    print(f"Error writing to .settings.json: {io_err}")