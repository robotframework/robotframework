class PythonClass:
    python_string = 'hello'
    python_integer = None
    LIST__python_list = ['a', 'b', 'c']

    def __init__(self):
        self.python_integer = 42

    def python_method(self):
        pass

    @property
    def python_property(self):
        return 'value'
