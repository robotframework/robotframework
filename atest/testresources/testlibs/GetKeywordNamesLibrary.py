from __future__ import print_function

from robot.api import deco


def passing_handler(*args):
    for arg in args:
        print(arg, end=' ')
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
        marked_keywords = [name for name in dir(self) if hasattr(getattr(self, name), 'robot_name')]
        other_keywords = ['Get Keyword That Passes', 'Get Keyword That Fails',
                          'keyword_in_library_itself', 'non_existing_kw',
                          'this_is_not_keyword']
        return marked_keywords + other_keywords

    def __getattr__(self, name):
        if name == 'Get Keyword That Passes':
            return passing_handler
        if name == 'Get Keyword That Fails':
            return failing_handler
        raise AttributeError("Non-existing keyword '%s'" % name)

    def keyword_in_library_itself(self):
        msg = 'No need for __getattr__ here!!'
        print(msg)
        return msg

    @deco.keyword('Name Set Using Robot Name Attribute')
    def name_set_in_method_signature(self):
        pass

    @deco.keyword
    def keyword_name_should_not_change(self):
        pass

    @deco.keyword('Add ${count} Copies Of ${item} To Cart')
    def add_copies_to_cart(self, count, item):
        return count, item
