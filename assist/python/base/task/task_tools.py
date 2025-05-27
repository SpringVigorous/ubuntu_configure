from typing import Callable

def until_success(func: Callable[..., any], max_retries=3, *args, **kwargs) -> bool:
    retries = 0
    while retries < max_retries:
        try:
            if bool(func(*args, **kwargs)):
                return True
        except Exception as e:
            print(e)
            continue
        finally:
            retries += 1
    return False


