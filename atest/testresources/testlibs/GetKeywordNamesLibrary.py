from robot.api.deco import keyword


def passing_handler(*args):
    for arg in args:
        print(arg, end=' ')
    return ', '.join(args)


def failing_handler(*args):
    raise AssertionError('Failure: %s' % ' '.join(args) if args else 'Failure')


class GetKeywordNamesLibrary:

    def __init__(self):
        self.not_method_or_function = 'This is just a string!!'

    def get_keyword_names(self):
        marked = [name for name in dir(self)
                  if hasattr(getattr(self, name), 'robot_name')]
        other = ['Get Keyword That Passes', 'Get Keyword That Fails',
                 'keyword_in_library_itself', '_starting_with_underscore_is_ok',
                 'Non-existing attribute', 'not_method_or_function',
                 'Unexpected error getting attribute']
        return marked + other

    def __getattr__(self, name):
        if name == 'Get Keyword That Passes':
            return passing_handler
        if name == 'Get Keyword That Fails':
            return failing_handler
        if name == 'Unexpected error getting attribute':
            raise TypeError('Oooops!')
        raise AttributeError("Non-existing attribute '%s'" % name)

    def keyword_in_library_itself(self):
        msg = 'No need for __getattr__ here!!'
        print(msg)
        return msg

    def _starting_with_underscore_is_ok(self):
        print("This is explicitly returned from 'get_keyword_names' anyway.")

    @keyword("Name set using 'robot_name' attribute")
    def name_set_in_method_signature(self):
        pass

    @keyword
    def keyword_name_should_not_change(self):
        pass

    @keyword('Add ${count} copies of ${item} to cart')
    def add_copies_to_cart(self, count, item):
        return count, item
