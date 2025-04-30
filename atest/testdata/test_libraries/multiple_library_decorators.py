from robot.api.deco import keyword, library


@library
class Class1:
    @keyword
    def class1_keyword(self):
        pass


@library(scope="SUITE")
class Class2:
    @keyword
    def class2_keyword(self):
        pass


@library
class Class3:
    @keyword
    def class3_keyword(self):
        pass


def module_keyword():
    pass
