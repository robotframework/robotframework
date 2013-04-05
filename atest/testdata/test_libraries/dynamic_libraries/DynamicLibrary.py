from impl_dynlib import impl_say_hello, impl_say_goodbye, impl_say_something_to, impl_a_keyword

KEYWORDS = {'say hello': (impl_say_hello, ['first_name=John']),
            'say goodbye': (impl_say_goodbye, ['first_name=John', 'last_name=Smith']),
            'say something to': (impl_say_something_to, ['message', 'to_whom=You', 'from_who=Me']),
            'a keyword': (impl_a_keyword, ['a', 'b=1'])}

class DynamicLibrary(object):

    def get_keyword_names(self):
        return KEYWORDS.keys()

    def run_keyword(self, kw_name, args):
        KEYWORDS[kw_name][0](*args)

    def get_keyword_arguments(self, kw_name):
        return KEYWORDS[kw_name][1]
