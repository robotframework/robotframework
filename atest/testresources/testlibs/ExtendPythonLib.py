from ExampleLibrary import ExampleLibrary


class ExtendPythonLib(ExampleLibrary):

    def kw_in_python_extender(self, arg):
        return arg/2

    def print_many(self, *msgs):
        raise Exception('Overridden kw executed!')

    def using_method_from_python_parent(self):
        self.exception('AssertionError', 'Error message from lib')
