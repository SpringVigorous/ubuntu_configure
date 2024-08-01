import __init__
from base.com_log import logger as logger
import base.file_tools as ft
import os
# 获取含有 指定内容 的的指定行信息，返回一个列表
def get_special_rows(orgstr:str,*flags):
    # rows=orgstr.split('/n')
    # result=[]
    # for row in rows:
    #     for flag in flags:
    #         if flag in row:
    #             result.append(row)
    # return result
    return [row.strip("\t\n\r ") for row in orgstr.split('\n') if any(flag in row for flag in flags)]
    
# 从文件中获取含有 指定内容 的的指定行信息，返回一个列表
def get_special_from_file(file_path,*flag):
    return get_special_rows(ft.read_content(file_path),*flag)


# import win32security
# import ntsecuritycon as con
# import os
# def backup_and_set_permissions(path, new_permissions):
#     # 备份原始权限
#     original_sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
#     original_dacl = original_sd.GetSecurityDescriptorDacl()

#     # 修改权限
#     sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
#     dacl = sd.GetSecurityDescriptorDacl()
    
#     # 添加Everyone组的读取权限
#     everyone, domain, type = win32security.LookupAccountName('', 'Everyone')
#     ace = win32security.ACL()
#     ace.AddAccessAllowedAce(win32security.ACL_REVISION, new_permissions, everyone)
#     dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, 0, new_permissions, everyone)
#     sd.SetSecurityDescriptorDacl(1, dacl, 0)
#     win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)

#     return original_sd

# def restore_permissions(path, original_sd):
#     # 恢复原始权限
#     win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, original_sd)







def get_special_from_file_list(file_list,*flag):
    result=[] 

    for file_path in file_list:
        # os.rename(file_path, f"{file_path}.txt")
        # return result
        
        # original_sd = None
        try:
            #临时修改权限，执行操作，然后恢复权限并删除
            # original_sd = backup_and_set_permissions(file_path, con.FILE_GENERIC_READ)
            result.extend(get_special_from_file(file_path,*flag))
        except FileNotFoundError:
            logger.error(f"Error: The {file_path} does not exist.")
        except PermissionError:
            logger.error(f"Error: Permission denied when trying to move '{file_path}' to the recycle bin.")
        except Exception as e:
            logger.error(f"Error {file_path}: {e}")
        finally:
            
            # 恢复原始权限
            # if original_sd is not None:
            #     restore_permissions(file_path, original_sd)
            pass
    return result




def get_special_from_dir(dir_path,sub_dir_filter:list,filename_fileter:list, *flag):
    import itertools
    if not os.path.isdir(dir_path):
        dir_path=os.path.dirname(dir_path)
    if not os.path.exists(dir_path):
        return []
    has_dir=sub_dir_filter is not None and len(sub_dir_filter)>0
    has_filter=filename_fileter is not None and len(filename_fileter)>0
    
    file_lists=[]

    
    
    for root, dirs, files in os.walk(dir_path,topdown=False):
        if has_dir and not any(dir in root for dir in sub_dir_filter):
            continue
        if has_filter and not any(file in files for file in filename_fileter):
            continue
        file_lists.extend([os.path.abspath( os.path.join(root,item)) for item in filename_fileter])
        
        
        
        # for pair in itertools.product(sub_dir_filter, filename_fileter):
        #     file_path=os.path.abspath( os.path.join(root, '/'.join(pair)))
        #     # stat_info = os.stat(file_path)
        #     # if os.path.exists(file_path):
        #     result.append(file_path)
    import json           
    logger.trace(f"筛选出的文件列表:\n{ json.dumps(file_lists,indent=4) }")
    results=get_special_from_file_list(file_lists,*flag)
    logger.trace(f"获得的结果行:\n{ json.dumps(results,indent=4) }")
    results=[item for item in results if item.find("boostorg")<0]
    logger.trace(f"过滤后的结果行:\n{ json.dumps(results,indent=4) }")

        # # 构建输出文件路径
        # for file in files:
        #     if has_filter and  not any(file.endswith(ext) for ext in filter_agrs):
        #         continue
        #     org_file_path = os.path.join(root, file)
        #     os.makedirs(dest_dir_path, exist_ok=True)
        #     dest_file_path=os.path.join(dest_dir_path, get_real_name(file))

        #     operate_imp(org_file_path, dest_file_path,dest_encoding,operate_func)


if __name__ == '__main__':
    rows=get_special_from_dir("f:/test",['.git'],["config"],"url = ")
    print(rows)