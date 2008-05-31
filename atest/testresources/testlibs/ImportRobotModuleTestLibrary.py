import os  # Tests that standard modules can be imported from libraries
import sys


class ImportRobotModuleTestLibrary:
    """Tests that robot internal modules can't be imported accidentally"""

    def import_logging(self):
        try:
            import logging
        except ImportError:
            if os.name == 'java':
                print 'Could not import logging, which is OK in Jython!'
                return
            raise AssertionError, 'Importing logging module failed with Python!'
        try:
            logger = logging.getLogger()
        except:
            raise AssertionError, 'Wrong logging module imported!'
        print 'Importing succeeded!'

    def importing_robot_module_directly_fails(self):        
        try:
            import serializing
        except ImportError:
            pass
        except:
            raise
        else:
            msg = "'import serializing' should have failed. Got it from '%s'. sys.path: %s"
            raise AssertionError, msg % (serializing.__file__, sys.path)

    def importing_robot_module_through_robot_succeeds(self):        
        try:
            import robot.running
        except:
            raise AssertionError, "'import robot.running' failed"