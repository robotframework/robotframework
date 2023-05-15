class TestLibrary:

    def __init__(self, name='TestLibrary'):
        self.name = name

    def get_name(self):
        return self.name

    get_library_name = get_name

    def no_operation(self):
        return self.name

def get_name_with_search_order(name):
    raise AssertionError('Should not be run due to search order '
                         'having higher precedence.')

def get_best_match_ever_with_search_order():
    raise AssertionError('Should not be run due to search order '
                         'having higher precedence.')    
