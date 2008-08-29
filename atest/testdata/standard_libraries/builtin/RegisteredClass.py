from robot.libraries.BuiltIn import BuiltIn, register_run_keyword


class RegisteredClass:
    def run_keyword_if_method(self, expression, name, *args):
        return BuiltIn().run_keyword_if(expression, name, *args)

    def run_keyword_method(self, name, *args):
        return BuiltIn().run_keyword(name, *args)

register_run_keyword("RegisteredClass", RegisteredClass.run_keyword_if_method)
register_run_keyword("RegisteredClass", "run_keyword_method", 1)