from robot.api.deco import not_keyword


class ClassWithNotKeywordDecorator:

    def exposed_in_class(self):
        pass

    @not_keyword
    def not_exposed_in_class(self):
        pass
