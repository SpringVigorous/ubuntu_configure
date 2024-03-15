def pipe(obj, *funcs):
    for func in funcs:
        obj = func(obj)
    return obj