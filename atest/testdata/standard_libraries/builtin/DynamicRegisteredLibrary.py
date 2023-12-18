from robot.libraries.BuiltIn import BuiltIn, register_run_keyword


class DynamicRegisteredLibrary:

    def get_keyword_names(self):
        return ['dynamic_run_keyword']

    def run_keyword(self, name, args):
        dynamic_run_keyword(*args)


def dynamic_run_keyword(name, *args):
    return BuiltIn().run_keyword(name, *args)


register_run_keyword('DynamicRegisteredLibrary', 'dynamic_run_keyword', 1,
                     deprecation_warning=False)
