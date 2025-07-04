from robot.api.deco import library


@library(auto_keywords=None)
class LibraryDecorator:

    def not_keyword_v3(self):
        raise RuntimeError("Should not be executed!")
