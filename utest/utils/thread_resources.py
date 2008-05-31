import os, time


class MyException(Exception):
    pass

def passing(*args):
    pass

def sleeping(s):
    time.sleep(s)
    os.environ['ROBOT_THREAD_TESTING'] = str(s)
    return s

def returning(arg):
    return arg

def failing(msg='xxx'):
    raise MyException, msg

if os.name == 'java':
    from java.lang import Error
    def java_failing(msg='zzz'):
        raise Error(msg)
