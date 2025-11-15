from setuptools import setup, find_packages

setup(
    name="hm_project",
    version="0.1",
    packages=find_packages()  # 自动发现 task 和 task1 包
)


# parent_dir/          # 父目录（task和task1的共同上级目录）
# ├── task/            # 独立包 task
# │   ├── __init__.py
# │   └── thread_task.py  # 含 ThreadTask、ResultThread
# └── task1/           # 独立包 task1（需要使用 task 中的内容）
#     ├── __init__.py
#     └── some_module.py  # 在这个文件中使用 task
# 将包安装为可编辑包（推荐用于项目开发）在 parent_dir 下创建 setup.py 或 pyproject.toml，将 task 和 task1 声明为可安装包，安装后可直接导入（无需手动处理路径）。示例 setup.py：
# python
# 运行
# from setuptools import setup, find_packages

# setup(
#     name="my_packages",
#     version="0.1",
#     packages=find_packages()  # 自动发现 task 和 task1 包
# )



# 然后在 parent_dir 下运行安装命令（开发模式，修改代码无需重新安装）：
# bash
# pip install -e .
# 安装后，任何地方都可直接导入：
# python
# 运行
# # task1/some_module.py
# from task.thread_task import ThreadTask  # 直接导入，无需额外配置路径