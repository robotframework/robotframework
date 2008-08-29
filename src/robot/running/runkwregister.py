from types import MethodType, FunctionType

from robot import utils


class _RunKeywordRegister:
    
    def __init__(self):
        self._register = {'IpaMml':{'Run Keyword If':2}}    
    
    def register_run_keyword(self, library, keyword, args_to_process=None):
        if args_to_process is None:            
            args_to_process = self._get_args_from_method(keyword)
            keyword =  keyword.__name__
        keyword = utils.printable_name(keyword, code_style=True)
        self._register.setdefault(library, {})[keyword] = int(args_to_process)
            
    def get_args_to_process(self, lib, keyword):
        if lib in self._register and keyword in self._register[lib]:
            return self._register[lib][keyword]
        return -1

    def _get_args_from_method(self, method):
        if type(method) is MethodType:
            return method.im_func.func_code.co_argcount -1
        elif type(method) is FunctionType:
            return method.func_code.co_argcount
        raise ValueError("Needs function or method!")


RUN_KW_REGISTER = _RunKeywordRegister()