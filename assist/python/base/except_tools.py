from output_agent import OutputAgent
import traceback
import sys
def except_stack()->str:
    # 这个except块会处理上述try块中的任何异常
    # 获取当前的异常信息
    _, exc_value, exc_traceback = sys.exc_info()


    err_detail=""

    agent = OutputAgent ()
    # 打印异常堆栈信息，其中包含了函数调用的文件信息
    traceback.print_tb(exc_traceback.tb_next)
    if agent.has_err:
        err_detail=agent.err_value
    agent.clear()
    
    lst=[f"{exc_value}",err_detail]
    
    return "\n".join(filter(lambda x:x,lst)) 