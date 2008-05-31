import ExampleJavaLibrary

class ExtendJavaLib(ExampleJavaLibrary):
    
    def kw_in_java_extender(self, arg):
        return arg*2
    
    def javaSleep(self, secs):
        raise Exception('Overridden kw executed!')
    
    def using_method_from_java_parent(self):
        self.divByZero()