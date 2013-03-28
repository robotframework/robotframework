from impl_dynlib import impl_say_hello, impl_say_goodbye, impl_say_something_to

KEYWORDS = {"say hello": (impl_say_hello, ["first_name=Ilmari"]),
            "say goodbye": (impl_say_goodbye, ["first_name=Ilmari", "last_name=Kontulainen"]),
            "say something to" : (impl_say_something_to, ["message", "to_whom"])}

class DynamicLibrary(object):

    def get_keyword_names(self):
        return KEYWORDS.keys()

    def run_keyword(self, kw_name, args):
        KEYWORDS[kw_name][0](*args)

    def get_keyword_arguments(self, kw_name):
        return KEYWORDS[kw_name][1]
