class ExampleObject:

    def __init__(self, name="<noname>"):
        self.name = name

    def greet(self, name=None):
        if not name:
            return f"{self.name} says hi!"
        if name == "FAIL":
            raise ValueError
        return f"{self.name} says hi to {name}!"

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)


OBJ = ExampleObject("dude")
