from robot.api.deco import keyword, library

# Imported decorated classes are not considered libraries automatically.
from LibraryDecorator import DecoratedLibraryToBeExtended
from multiple_library_decorators import Class1, Class2, Class3


@library(version='extended')
class ExtendedLibrary(DecoratedLibraryToBeExtended):

    @keyword
    def keyword_in_decorated_extending_class(self):
        pass
