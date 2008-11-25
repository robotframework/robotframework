class no_arg_init:

    def __init__(self):
        """This doc not shown because there are no arguments."""

    def keyword(self):
        """A keyword.

        See `get hello` for details and *never* run this keyword.
        """
        1/0

    def get_hello(self, arg):
        """Returns 'Hello `arg`!'.

        See `initialization` for explanation of arguments and `introduction`
        for introduction. Neither of them really exist, though.
        """
        return 'Hello %s' % arg

