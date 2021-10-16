from robot.api.deco import keyword


class InvalidKeywords:

    @keyword('Invalid embedded ${args}')
    def invalid_embedded(self):
        pass

    def duplicate_name(self):
        pass

    def duplicateName(self):
        pass

    @keyword('Same ${embedded}')
    def dupe_with_embedded_1(self, arg):
        pass

    @keyword('same ${match}')
    def dupe_with_embedded_2(self, arg):
        """This is an error only at run time."""
        pass
