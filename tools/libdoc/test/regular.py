class regular:
    """This is a very regular test library"""

    def __init__(self, arg1='hello', arg2='world'):
        """Constructs a new regular test library

        See `keyword`

        Examples:
        
        | regular | foo | bar |
        | regular |     | # default values are used |
        """
        self.arg1 = arg1
        self.arg2 = arg2

    def keyword(self):
        """A "keyword" & it contains 'stuff' to <escape> 

        See `get hello` for details"""
        pass

    def get_hello(self):
        """Get the intialization variables

        See `importing` for explanation of arguments
        and `introduction` for introduction"""
        return self.arg1, self.arg2
