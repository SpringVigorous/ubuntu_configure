# 常用工具

## 创建本地环境****

1. 创建
   python -m venv myenv
2. 激活
   win: 	myenv\Scripts\activate
   linux/mac:	source myenv/bin/activate

## 导出所有pip安装的包

pip freeze > requirements.txt


| 场景                 | 推荐命令                                      | 说明                                                             |
| -------------------- | --------------------------------------------- | ---------------------------------------------------------------- |
| **标准导出**         | `pip freeze > requirements.txt`               | 最常用，导出所有包19。                                           |
| **生成更规范列表**   | `pip list --format=freeze > requirements.txt` | 某些情况下格式更规范811。                                        |
| **仅导出项目必要包** | `pipreqs ./ --encoding=utf8`                  | 需先`pip install pipreqs`，只导出项目实际import的包，更精简689。 |
| **使用Conda环境**    | `conda env export > environment.yml`          | 如果myenv是Conda环境，用此命令可导出更完整的环境信息679。        |
