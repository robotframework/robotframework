import ExampleJavaLibrary
import JavaVarArgsConstructor


class ExtendJavaLib(ExampleJavaLibrary):
    
    def kw_in_java_extender(self, arg):
        return arg*2
    
    def javaSleep(self, secs):
        raise Exception('Overridden kw executed!')
    
    def using_method_from_java_parent(self):
        self.divByZero()
        
        
class ExtendJavaLibWithConstructor(JavaVarArgsConstructor):
    
    def keyword(self):
        return None


class ExtendJavaLibWithInit(ExampleJavaLibrary):
    
    def __init__(self, *args):
        self.args = args
        
    def get_args(self):
        return self.args
    

class ExtendJavaLibWithInitAndConstructor(JavaVarArgsConstructor):
    
    def __init__(self, *args):
        if len(args) == 1:
            JavaVarArgsConstructor.__init__(self, args[0])
        self.kw = lambda self: "Hello, world!"
    
    