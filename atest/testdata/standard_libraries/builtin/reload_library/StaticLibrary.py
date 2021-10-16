from robot.libraries.BuiltIn import BuiltIn


class StaticLibrary:

    def add_static_keyword(self, name):
        def f(x):
            """This doc for static"""
            return x
        setattr(self, name, f)
        BuiltIn().reload_library(self)
