class ObjectToReturn:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def exception(self, name, msg=""):
        try:
            exception = getattr(__builtins__, name)
        except AttributeError:  # __builtins__ is sometimes a dict, go figure
            exception = __builtins__[name]
        raise exception(msg)
