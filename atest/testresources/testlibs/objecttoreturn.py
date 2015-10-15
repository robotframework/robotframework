class ObjectToReturn:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def exception(self, name, msg=""):
        exception = __builtins__[name]
        raise exception(msg)
