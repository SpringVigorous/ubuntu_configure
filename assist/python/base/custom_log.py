import os
import io
import traceback
import logging
from pathlib import Path


class CustomLogger(logging.Logger):
    def findCaller(self, stack_info=False, stacklevel=1):
        """
        重写 findCaller 方法以确保获取正确的调用者信息。
        """
        frame = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if frame is not None:
            frame = frame.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(frame, "f_code"):
            co = frame.f_code
            filename = os.path.normcase(co.co_filename) 
            if filename == logging._srcfile or Path(filename).name in ("custom_log.py","com_log.py"):
                frame = frame.f_back
                continue

            
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f=frame, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, frame.f_lineno, co.co_name, sinfo)
            break
        return rv

# 注册自定义的 Logger 类
logging.setLoggerClass(CustomLogger)



