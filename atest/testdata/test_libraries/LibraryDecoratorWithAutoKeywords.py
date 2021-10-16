from robot.api.deco import keyword, library


@library(scope='global', auto_keywords=True)
class LibraryDecoratorWithAutoKeywords:

    def undecorated_method_is_keyword(self):
        pass

    @keyword
    def decorated_method_is_keyword_as_well(self):
        pass
