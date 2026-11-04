import unittest

from robot.output.listeners import ListenerFacade
from robot.output.logger import Logger
from robot.output.loggerapi import LoggerApi
from robot.running.resourcemodel import Import


class TestPreImportListenerFacade(unittest.TestCase):

    def test_listener_v3_exposes_pre_import_events_with_importer(self):
        class Listener:
            ROBOT_LISTENER_API_VERSION = 3

            def start_library_import(self, importer):
                importer.name = "ChangedLibrary"

            def start_resource_import(self, importer):
                importer.name = "changed.resource"

            def start_variables_import(self, importer):
                importer.args = ("changed",)

        listener = ListenerFacade.create(Listener())
        library = Import(Import.LIBRARY, "OriginalLibrary")
        resource = Import(Import.RESOURCE, "original.resource")
        variables = Import(Import.VARIABLES, "original.py", ("original",))

        listener.start_library_import(library)
        listener.start_resource_import(resource)
        listener.start_variables_import(variables)

        assert library.name == "ChangedLibrary"
        assert resource.name == "changed.resource"
        assert variables.args == ("changed",)


class TestLoggerPreImport(unittest.TestCase):

    def test_logger_forwards_pre_import_event_to_registered_logger(self):
        received = []

        class LoggerUnderTest(LoggerApi):
            def start_library_import(self, importer):
                received.append(importer)

        logger = Logger(register_console_logger=False)
        logger.register_logger(LoggerUnderTest())
        importer = Import(Import.LIBRARY, "Library")

        logger.start_library_import(importer)

        self.assertEqual(received, [importer])
