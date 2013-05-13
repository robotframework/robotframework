class InitializationFailLibrary:

    def __init__(self, arg1='default 1', arg2='default 2'):
        raise Exception("Initialization failed with arguments %r and %r!" % (arg1, arg2))
