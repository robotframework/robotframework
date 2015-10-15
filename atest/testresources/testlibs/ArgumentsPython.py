class ArgumentsPython:

    # method docs are used in unit tests as expected min and max args

    def a_0(self):
        """(0,0)"""
        return 'a_0'

    def a_1(self, arg):
        """(1,1)"""
        return 'a_1: ' + arg

    def a_3(self, arg1, arg2, arg3):
        """(3,3)"""
        return ' '.join(['a_3:',arg1,arg2,arg3])

    def a_0_1(self, arg='default'):
        """(0,1)"""
        return 'a_0_1: ' + arg

    def a_1_3(self, arg1, arg2='default', arg3='default'):
        """(1,3)"""
        return ' '.join(['a_1_3:',arg1,arg2,arg3])

    def a_0_n(self, *args):
        """(0,sys.maxsize)"""
        return ' '.join(['a_0_n:', ' '.join(args)])

    def a_1_n(self, arg, *args):
        """(1,sys.maxsize)"""
        return ' '.join(['a_1_n:', arg, ' '.join(args)])

    def a_1_2_n(self, arg1, arg2='default', *args):
        """(1,sys.maxsize)"""
        return ' '.join(['a_1_2_n:', arg1, arg2, ' '.join(args)])
