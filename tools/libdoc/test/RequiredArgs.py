class RequiredArgs:

    def __init__(self, required, arguments, default="value"):
        """This library always needs two arguments and has one default.

        Keyword names are got from the given arguments.
        """
        self.__dict__[required] = lambda: None
        self.__dict__[arguments] = lambda arg: None
        self.__dict__[default] = lambda arg1, arg2: None

