from robot.api.deco import keyword, library


@library(version='3.2b1', scope='GLOBAL', doc_format='HTML')
class LibraryDecorator:
    ROBOT_LIBRARY_VERSION = 'overridden'

    @keyword
    def kw(self):
        pass

    def not_kw(self):
        pass
