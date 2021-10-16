from robot.libraries.BuiltIn import BuiltIn

class NamespaceUsingLibrary:

    def __init__(self):
        self._importing_suite = BuiltIn().get_variable_value('${SUITE NAME}')
        self._easter = BuiltIn().get_library_instance('Easter')

    def get_importing_suite(self):
        return self._importing_suite

    def get_other_library(self):
        return self._easter
