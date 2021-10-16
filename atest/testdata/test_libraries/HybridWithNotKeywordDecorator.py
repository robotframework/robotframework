from robot.api.deco import not_keyword


class HybridWithNotKeywordDecorator:

    def get_keyword_names(self):
        return ['exposed_in_hybrid', 'not_exposed_in_hybrid']

    def exposed_in_hybrid(self):
        pass

    @not_keyword
    def not_exposed_in_hybrid(self):
        pass
