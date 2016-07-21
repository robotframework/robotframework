def add_module_keyword(name):
    def f(x):
        """This doc for module"""
        return x
    globals()[name] = f

