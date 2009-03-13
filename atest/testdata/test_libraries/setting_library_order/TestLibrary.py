class TestLibrary:
    
    def __init__(self, name):
        self.name = name
        
    def get_name(self):
        return self.name
    
    def no_operation(self):
        raise AssertionError("No operation used in TestLibrary!")
