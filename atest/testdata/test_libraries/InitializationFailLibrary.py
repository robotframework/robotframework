class InitializationFailLibrary:

    def __init__(self, arg1="default 1", arg2="default 2"):
        raise Exception(f"Initialization failed with arguments {arg1!r} and {arg2!r}!")
