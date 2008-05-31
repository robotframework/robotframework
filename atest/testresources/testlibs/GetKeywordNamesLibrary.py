from robot import utils


def passing_handler(*args):
    for arg in args:
        print arg,
    return ', '.join(args)

def failing_handler(*args):
    if len(args) == 0:
        msg = 'Failure'
    else:
        msg = 'Failure: %s' % ' '.join(args)
    raise AssertionError(msg)


class GetKeywordNamesLibrary:
    
    def __init__(self):
        self.this_is_not_keyword = 'This is just an attribute!!'
    
    def get_keyword_names(self):
        return ['Get Keyword That Passes', 'Get Keyword That Fails',
                'keyword_in_library_itself', 'non_existing_kw',
                'this_is_not_keyword']
    
    def __getattr__(self, name):
        if name == 'Get Keyword That Passes':
            return passing_handler
        if name == 'Get Keyword That Fails':
            return failing_handler
        raise AttributeError("Non-existing keyword '%s'" % name)
        
    def keyword_in_library_itself(self):
        msg = 'No need for __getattr__ here!!'
        print msg
        return msg
