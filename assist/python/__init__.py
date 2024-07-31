from add_path import add_parent_path_by_file,add_sub_path_by_file
# 将当前脚本所在项目的根路径添加到sys.path

# 添加搜索路径
add_sub_path_by_file(__file__, "base","integer")