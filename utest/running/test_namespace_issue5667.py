import unittest

from robot.running import namespace
from robot.running.namespace import Namespace
from robot.running.resourcemodel import Import


class FakeVariables:

    def replace_string(self, value):
        return value

    def replace_list(self, values):
        return list(values)

    def set_from_variable_section(self, variables, overwrite):
        pass

    def set_from_file(self, path, args, overwrite):
        pass


class FakeKeywordStore:

    def __init__(self):
        self.libraries = {}
        self.resources = {}


class FakeScopeManager:

    def start_suite(self):
        pass


class FakeLibrary:

    name = "ImportedLibrary"
    real_name = "OriginalLibrary"
    source = None

    def __init__(self):
        self.init = type("Init", (), {"positional": (), "named": {}})()
        self.scope_manager = FakeScopeManager()


class FakeResource:

    name = "changed.resource"
    source = None
    variables = ()
    imports = ()


class FakeImporter:

    def __init__(self, events):
        self.events = events

    def import_library(self, name, args, alias, variables):
        self.events.append(("library", name, tuple(args), alias))
        return FakeLibrary()

    def import_resource(self, path, languages):
        self.events.append(("resource", path))
        return FakeResource()


class PreImportLogger:

    def __init__(self, events):
        self.events = events

    def start_library_import(self, importer):
        self.events.append("start_library")
        importer.name = "ChangedLibrary"
        importer.args = ("changed-arg",)
        importer.alias = "ChangedAlias"

    def start_resource_import(self, importer):
        self.events.append("start_resource")
        importer.name = "changed.resource"

    def start_variables_import(self, importer):
        self.events.append("start_variables")
        importer.name = "changed.py"
        importer.args = ("changed-arg",)

    def library_import(self, library, importer):
        self.events.append("end_library")

    def resource_import(self, resource, importer):
        self.events.append("end_resource")

    def variables_import(self, variables, importer):
        self.events.append("end_variables")


def _namespace(events):
    ns = Namespace.__new__(Namespace)
    ns.variables = FakeVariables()
    ns.languages = object()
    ns._kw_store = FakeKeywordStore()
    ns._imported_variable_files = namespace.ImportCache()
    ns._suite_name = "suite"
    ns._running_test = False
    ns._resolve_name = lambda import_: import_.name
    ns._resolve_args = lambda import_: tuple(import_.args)
    return ns


class TestNamespacePreImport(unittest.TestCase):

    def test_pre_import_events_mutate_all_import_types_before_import(self):
        events = []
        original_logger = namespace.LOGGER
        original_importer = namespace.IMPORTER
        namespace.LOGGER = PreImportLogger(events)
        namespace.IMPORTER = FakeImporter(events)
        try:
            ns = _namespace(events)

            ns._import_library(Import(Import.LIBRARY, "OriginalLibrary", ("original",), "OriginalAlias"))
            ns._import_resource(Import(Import.RESOURCE, "original.resource"))
            ns._import_variables(Import(Import.VARIABLES, "original.py", ("original",)))

            self.assertEqual(events, [
                "start_library",
                ("library", "ChangedLibrary", ("changed-arg",), "ChangedAlias"),
                "end_library",
                "start_resource",
                ("resource", "changed.resource"),
                "end_resource",
                "start_variables",
                "end_variables",
            ])
        finally:
            namespace.LOGGER = original_logger
            namespace.IMPORTER = original_importer
