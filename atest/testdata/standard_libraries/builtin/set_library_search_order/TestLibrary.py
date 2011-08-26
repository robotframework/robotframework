class TestLibrary:
    
    def __init__(self, name='TestLibrary'):
        self.name = name
        
    def get_name(self):
        return self.name

    get_library_name = get_name

    def no_operation(self):
        raise AssertionError("No operation used in %s!" % self.name)

