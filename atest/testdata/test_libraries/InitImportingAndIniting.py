from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


class Importing:

    def __init__(self):
        BuiltIn().import_library("String")

    def kw_from_lib_with_importing_init(self):
        print("Keyword from library with importing __init__.")


class Initting:

    def __init__(self):
        self.lib = BuiltIn().get_library_instance("InitImportingAndIniting.Initted")

    def kw_from_lib_with_initting_init(self):
        logger.info("Keyword from library with initting __init__.")
        self.lib.kw_from_lib_initted_by_init()


class Initted:

    def __init__(self, id):
        self.id = id

    def kw_from_lib_initted_by_init(self):
        print(f"Keyword from library initted by __init__ (id: {self.id}).")
