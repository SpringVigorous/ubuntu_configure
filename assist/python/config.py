
from dynaconf import Dynaconf,DjangoDynaconf,loaders 
import json


# dynaconf -i config.settings list

from jinja2 import Environment, FileSystemLoader
import yaml

# # 创建一个 Jinja2 环境用于渲染模板
# jinja_env = Environment(loader=FileSystemLoader('.'))
# def render_jinja2_template(filename):
#     template = jinja_env.get_template(filename)
#     rendered_config_str = template.render()  # 假设你已经正确注入了模板需要的环境变量等数据
#     return rendered_config_str

# class RenderedYamlLoader(loaders.yaml_loader):
#     def load(self, filename, **kwargs):
#         rendered_yaml_content = render_jinja2_template(filename)
#         loaded_config = yaml.safe_load(rendered_yaml_content)  # 将渲染后的字符串转换为 Python 字典
#         return loaded_config







settings = Dynaconf(
    env_switcher="LAUNCH_ENV",
    envvar_prefix="DYNACONF",
    # settings_files=['config/settings.toml', 'config/.secrets.toml'],
    settings_files=['config/settings.yaml'],
    environments=True,
    # 环境变量前缀，环境变量导出方式 `export CONF_FOO=bar` 变成 `settings.foo == "bar"`
    # envvar_prefix="CONFIG",
    lowercase_read=True,
    # loaders=[RenderedYamlLoader()],
    # yaml_loader="safe_load",
)
# settings1 = DjangoDynaconf(__name__) # noqa
# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
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