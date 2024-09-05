import os
import sys

__parent_dir__=os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
if __parent_dir__ not in sys.path:
    sys.path.append(__parent_dir__)

from add_path import add_parent_path_by_file

def add_base_path(file_path,*args):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(file_path), os.path.pardir)))
    add_parent_path_by_file(file_path, "base",*args)
    # print(sys.path)


add_base_path(__file__)

__all__=["RoutineTask","CoroutineTask","ThreadTask","ProcessTask"]