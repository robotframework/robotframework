Parser interface
================

Robot Framework supports external parsers that can handle custom data formats or
even override Robot Framework's own parser.

.. note:: Custom parsers are new in Robot Framework 6.1.

.. contents::
   :depth: 2
   :local:

Taking parsers into use
-----------------------

Parsers are taken into use from the command line with the :option:`--parser`
option using exactly the same semantics as with listeners__. This includes
specifying parsers as names or paths, giving arguments to parser classes, and
so on::

    robot --parser MyParser tests.custom
    robot --parser path/to/MyParser.py tests.custom
    robot --parser Parser1:arg --parser Parser2:a1:a2 path/to/tests

__ `Registering listeners from command line`_

Parser API
----------

Parsers can be implemented both as modules and classes. This section explains
what attributes and methods they must contain.

`EXTENSION` or `extension` attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This attribute specifies what file extension or extensions the parser supports.
Both `EXTENSION` and `extension` names are accepted, and the former has precedence
if both exist. The attribute can be either a string or a sequence of strings.
Extensions are case-insensitive and can be specified with or without the leading
dot. If a parser is implemented as a class, it is possible to set this attribute
either as a class attribute or as an instance attribute.

Also extensions containing multiple parts like :file:`.example.ext` or
:file:`.robot.zip` are supported.

.. note:: If a parser supports the :file:`.robot` extension, it will be used
          for parsing these files instead of the standard parser.

`parse` method
~~~~~~~~~~~~~~

The mandatory `parse` method is responsible for parsing `suite files`_. It is
called with each parsed file that has an extension that the parser supports.
The method must return a `TestSuite <running.TestSuite_>`__ object.

In simple cases `parse` can be implemented so that it accepts just a single
argument that is a `pathlib.Path <pathlib_>`__ object pointing to the file to
parse. If the parser is interested in defaults for :setting:`Test Setup`,
:setting:`Test Teardown`, :setting:`Test Tags` and :setting:`Test Timeout`
set in higher level `suite initialization files`_, the `parse` method must
accept two arguments. In that case the second argument is a TestDefaults_ object.

.. _TestDefaults: https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.builder.html#robot.running.builder.settings.TestDefaults

`parse_init` method
~~~~~~~~~~~~~~~~~~~

The optional `parse_init` method is responsible for parsing `suite initialization
files`_ i.e. files in format `__init__.ext` where `.ext` is an extension
supported by the parser. The method must return a `TestSuite <running.TestSuite_>`__
object representing the whole directory. Suites created from child suite files
and directories will be added to its child suites.

Also `parse_init` can be implemented so that it accepts one or two arguments,
depending on is it interested in test related default values or not. If it
accepts defaults, it can manipulate the passed TestDefaults_ object and changes
are seen when parsing child suite files.

This method is only needed if a parser needs to support suite initialization files.

Optional base class
~~~~~~~~~~~~~~~~~~~

Parsers do not need to implement any explicit interface, but it may be helpful
to extend the optional Parser_ base class. The main benefit is that the base
class has documentation and type hints. It also works as a bit more formal API
specification.

.. _Parser: https://robot-framework.readthedocs.io/en/master/autodoc/robot.api.html#robot.api.interfaces.Parser

Examples
--------

Parser implemented as module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first example demonstrates a simple parser implemented as a module and
supporting one hard-coded extension. It just creates a dummy suite and does not
actually parse anything.

.. sourcecode:: python

    from robot.api import TestSuite


    EXTENSION = '.example'


    def parse(source):
        suite = TestSuite(name='Example', source=source)
        test = suite.tests.create(name='Test')
        test.body.create_keyword(name='Log', args=['Hello!'])
        return suite

Parser implemented as class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second parser is implemented as a class that accepts the extension to use
as an argument. The parser reads the given source file and creates dummy tests
from each line it contains.

.. sourcecode:: python

    from pathlib import Path
    from robot.api import TestSuite


    class ExampleParser:

        def __init__(self, extension: str):
            self.extension = extension

        def parse(self, source: Path) -> TestSuite:
            name = TestSuite.name_from_source(source, self.extension)
            suite = TestSuite(name, source=source)
            for line in source.read_text().splitlines():
                test = suite.tests.create(name=line)
                test.body.create_keyword(name='Log', args=['Hello!'])
            return suite

Parser extending optional base class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This parser extends the optional Parser_ base class. It supports parsing suite
initialization files, uses TestDefaults_ and registers multiple extensions.

.. sourcecode:: python

    from pathlib import Path
    from robot.api import TestSuite
    from robot.api.interfaces import Parser, TestDefaults


    class ExampleParser(Parser):
        extension = ('example', 'another')

        def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
            """Create a suite and set possible defaults from init files to tests."""
            suite = TestSuite(TestSuite.name_from_source(source), source=source)
            for line in source.read_text().splitlines():
                test = suite.tests.create(name=line, doc='Example')
                test.body.create_keyword(name='Log', args=['Hello!'])
                defaults.set_to(test)
            return suite

        def parse_init(self, source: Path, defaults: TestDefaults) -> TestSuite:
            """Create a dummy suite and set some defaults.

            This method is called only if there is an initialization file with
            a supported extension.
            """
            defaults.tags = ('tags', 'from init')
            defaults.setup = {'name': 'Log', 'args': ['Hello from init!']}
            return TestSuite(TestSuite.name_from_source(source.parent), doc='Example',
                             source=source, metadata={'Example': 'Value'})

Parser as preprocessor
~~~~~~~~~~~~~~~~~~~~~~

The final example parser acts as a preprocessor for Robot Framework data files
that supports headers in format `=== Test Cases ===` in addition to
`*** Test Cases ***`. In this kind of usage it is convenient to use
`TestSuite.from_string`__, `TestSuite.from_model`__ and
`TestSuite.from_file_system`__ factory methods for constructing the returned suite.

.. sourcecode:: python

    from pathlib import Path
    from robot.running import TestDefaults, TestSuite


    class RobotPreprocessor:
        extension = '.robot'

        def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
            data = source.read_text()
            for header in 'Settings', 'Variables', 'Test Cases', 'Keywords':
                data = data.replace(f'=== {header} ===', f'*** {header} ***')
            suite = TestSuite.from_string(data, defaults=defaults)
            return suite.config(name=TestSuite.name_from_source(source), source=source)

__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.html#robot.running.model.TestSuite.from_string
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.html#robot.running.model.TestSuite.from_model
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.html#robot.running.model.TestSuite.from_file_system
