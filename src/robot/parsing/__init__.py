#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

r"""Module implementing test data parsing.

Exposed API
-----------

The publicly exposed parsing entry points are the following:

* :func:`~.lexer.lexer.get_tokens`,
  :func:`~.lexer.lexer.get_resource_tokens`, and
  :func:`~.lexer.lexer.get_init_tokens` functions for tokenizing data.

* :class:`~.lexer.tokens.Token` class that contains all token types as
  class attributes.

* :func:`~.parser.parser.get_model`,
  :func:`~.parser.parser.get_resource_model`, and
  :func:`~.parser.parser.get_init_model` functions for getting a higher
  level model represented as an abstract syntax tree (AST).

.. tip:: Like with rest of the public API, these functions and classes are
         exposed also via the :mod:`robot.api` package. When they are used
         by external code, it is recommended they are imported like
         ``from robot.api import get_tokens``.

.. note:: The :mod:`robot.parsing` package has been totally rewritten in
          Robot Framework 3.2 and all code using it needs to be updated.
          Depending on the use case, it may be possible to instead use the
          higher level :func:`~robot.running.builder.builders.TestSuiteBuilder`
          that has only seen minor configuration changes.

Parsing data to tokens
----------------------

Data can be parsed to tokens by using
:func:`~.lexer.lexer.get_tokens`,
:func:`~.lexer.lexer.get_resource_tokens` or
:func:`~.lexer.lexer.get_init_tokens` functions depending on does the data
represent a test case (or task) file, a resource file, or a suite
initialization file. In practice the difference between these functions is
what settings and sections are valid.

Typically the data is easier to inspect and modify by using the higher level
model discussed in the next section, but in some cases the token stream can
be enough. Tokens returned by the aforementioned functions are
:class:`~.lexer.tokens.Token` instances and they have the token type, value,
and position easily available as their attributes. Tokens also have useful
string representation used by the example below::

    from robot.api import get_tokens

    path = 'example.robot'

    for token in get_tokens(path):
        print(repr(token))

If the :file:`example.robot` used by the above example would contain

.. code-block:: robotframework

    *** Test Cases ***
    Example
        Keyword    argument

    Second example
        Keyword    xxx

    *** Keywords ***
    Keyword
        [Arguments]    ${arg}
        Log    ${arg}

then the beginning of the output got when running the earlier code would
look like this::

    Token(TESTCASE_HEADER, '*** Test Cases ***', 1, 0)
    Token(EOL, '\n', 1, 18)
    Token(EOS, '', 1, 19)
    Token(TESTCASE_NAME, 'Example', 2, 0)
    Token(EOL, '\n', 2, 7)
    Token(EOS, '', 2, 8)
    Token(SEPARATOR, '    ', 3, 0)
    Token(KEYWORD, 'Keyword', 3, 4)
    Token(SEPARATOR, '    ', 3, 11)
    Token(ARGUMENT, 'argument', 3, 15)
    Token(EOL, '\n', 3, 23)
    Token(EOS, '', 3, 24)
    Token(EOL, '\n', 4, 0)
    Token(EOS, '', 4, 1)

The output shows token type, value, line number and column offset. The
``EOL`` tokens denote end of a line and they include the new line character
and possible trailing spaces. The ``EOS`` tokens denote end of a logical
statement. Typically a single line forms a statement, but when the ``...``
syntax is used for continuation, a statement spans multiple lines. In
special cases a single line can also contain multiple statements.

See the documentation of :func:`~.lexer.lexer.get_tokens` for details
about different ways how to specify the data to be parsed, how to control
should all tokens or only data tokens be returned, and should variables in
keyword arguments and elsewhere be tokenized or not.

Parsing data to model
---------------------

Data can be parsed to a higher level model by using
:func:`~.parser.parser.get_model`,
:func:`~.parser.parser.get_resource_model`, or
:func:`~.parser.parser.get_init_model` functions depending on the data
type same way as when `parsing data to tokens`_.

The model is represented as an abstract syntax tree (AST) implemented on top
of Python's standard `ast.AST`_ class. The ast_ module can also be used
for inspecting and modifying the module. Most importantly, `ast.NodeVisitor`_
and `ast.NodeTransformer`_ ease traversing the model as explained in the
sections below. The `ast.dump()`_ function, or the third-party astpretty_
module, can be used for debugging::

    import ast
    import astpretty    # third-party module
    from robot.api import get_model

    model = get_model('example.robot')
    print(ast.dump(model))
    print('-' * 72)
    astpretty.pprint(model)

Running this code with the :file:`example.robot` file from the previous
section would produce so much output that it is not included here. If
you are going to work with Robot Framework's AST, you are recommended to
try this on your own.

The model is build from blocks like
:class:`~.model.blocks.File` (the root of the model),
:class:`~.model.blocks.TestCaseSection`, and
:class:`~.model.blocks.TestCase`
implemented in the :mod:`~.model.blocks` module and from statements like
:class:`~.model.statements.TestCaseSectionHeader`,
:class:`~.model.statements.Documentation`, and
:class:`~.model.statements.KeywordCall`
implemented in the :mod:`~.model.statements` module.
Both blocks and statements are AST nodes based on `ast.AST`_.
Blocks can contain other blocks and statements as child nodes whereas
statements have only tokens. These tokens contain the actual data
represented as :class:`~.lexer.tokens.Token` instances.

.. _ast: https://docs.python.org/library/ast.html
.. _ast.AST: https://docs.python.org/library/ast.html#ast.AST
.. _ast.NodeVisitor: https://docs.python.org/library/ast.html#ast.NodeVisitor
.. _ast.NodeTransformer: https://docs.python.org/library/ast.html#ast.NodeTransformer
.. _ast.dump(): https://docs.python.org/library/ast.html#ast.dump
.. _astpretty: https://pypi.org/project/astpretty

Inspecting model
''''''''''''''''

The easiest way to inspect what data a model contains is implementing
a visitor based on `ast.NodeVisitor`_ and implementing ``visit_NodeName``
methods as needed. The following example illustrates how to find what tests
a certain test case file contains::

    import ast
    from robot.api import get_model


    class TestNamePrinter(ast.NodeVisitor):

        def visit_File(self, node):
            print(f"File '{node.source}' has following tests:")
            # Must call `generic_visit` to visit also child nodes.
            self.generic_visit(node)

        def visit_TestCaseName(self, node):
            print(f"- {node.name} (on line {node.lineno})")


    model = get_model('example.robot')
    printer = TestNamePrinter()
    printer.visit(model)

When the above code is run using the earlier :file:`example.robot`, the
output is this::

    File 'example.robot' has following tests:
    - Example (on line 2)
    - Second example (on line 5)

Modifying token values
''''''''''''''''''''''

The model can be modified simply by modifying token values. If changes need
to be saved, that is as easy as calling the :meth:`~.model.blocks.File.save`
method of the root model object. When just modifying token values, it is
possible to still extend `ast.NodeVisitor`_. The next section discusses
adding or removing nodes and then `ast.NodeTransformer`_ should be used
instead.

Modifications to tokens obviously require finding the tokens to be modified.
The first step is finding statements containing the tokens by implementing
needed ``visit_StatementName`` methods. Then the exact token or tokens
can be found using node's
:meth:`~.model.statements.Statement.get_token` or
:meth:`~.model.statements.Statement.get_tokens` methods.
If only token values are needed,
:meth:`~.model.statements.Statement.get_value` or
:meth:`~.model.statements.Statement.get_values` can be used as a shortcut.
First finding statements and then the right tokens is illustrated by
this example that renames keywords::

    import ast
    from robot.api import get_model, Token


    class KeywordRenamer(ast.NodeVisitor):

        def __init__(self, old_name, new_name):
            self.old_name = self.normalize(old_name)
            self.new_name = new_name

        def normalize(self, name):
            return name.lower().replace(' ', '').replace('_', '')

        def visit_KeywordName(self, node):
            # Rename keyword definitions.
            if self.normalize(node.name) == self.old_name:
                token = node.get_token(Token.KEYWORD_NAME)
                token.value = self.new_name

        def visit_KeywordCall(self, node):
            # Rename keyword usages.
            if self.normalize(node.keyword) == self.old_name:
                token = node.get_token(Token.KEYWORD)
                token.value = self.new_name


    model = get_model('example.robot')
    renamer = KeywordRenamer('Keyword', 'New Name')
    renamer.visit(model)
    model.save()

If you run the above example using the earlier :file:`example.robot`, you
can see that the ``Keyword`` keyword has been renamed to ``New Name``. Notice
that a real keyword renamer needed to take into account also keywords used
with setups, teardowns and templates.

When token values are changed, column offset of the other tokens on same
line are likely to be wrong. This does not affect saving the model or other
typical usages, but if it is a problem then the caller needs to updated
offsets separately.

Adding and removing nodes
-------------------------

Bigger changes to model are somewhat more complicated than just modifying
existing token values. When doing this kind of changes, `ast.NodeTransformer`_
needs to be used instead of `ast.NodeVisitor`_ that was used in earlier
examples.

Removing nodes is relative easy and is accomplished by returning ``None``
from ``visit_NodeName`` methods. Remember to return the original node,
or possibly a replacement node, from all of these methods when you do not
want a node to be removed.

Adding nodes is unfortunately not supported by the public :mod:`robot.api`
interface and the needed block and statement nodes need to be imported
via the :mod:`robot.parsing.model` package. That package is considered
private and may change in the future. A stable public API can be added,
and functionality related to adding nodes improved in general, if there
are concrete needs for this kind of advanced usage.

The following example demonstrates both removing and adding nodes.
If you run it against the earlier :file:`example.robot`, you see that
the first test gets a new keyword, the second test is removed, and
settings section with documentation is added.

::

    import ast
    from robot.api import get_model, Token
    from robot.parsing.model import SettingSection, Statement


    class TestModifier(ast.NodeTransformer):

        def visit_TestCase(self, node):
            # The matched `TestCase` node is a block with `header` and `body`
            # attributes. `header` is a statement with familiar `get_token` and
            # `get_value` methods for getting certain tokens or their value.
            name = node.header.get_value(Token.TESTCASE_NAME)
            # Returning `None` drops the node altogether i.e. removes this test.
            if name == 'Second example':
                return None
            # Construct new keyword call statement from tokens.
            new_keyword = Statement.from_tokens([
                Token(Token.SEPARATOR, '    '),
                Token(Token.KEYWORD, 'New Keyword'),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'xxx'),
                Token(Token.EOL, '\n')
            ])
            # Add the keyword call to test as the second item. `body` is a list.
            node.body.insert(1, new_keyword)
            # No need to call `generic_visit` because we are not modifying child
            # nodes. The node itself must to be returned to avoid dropping it.
            return node

        def visit_File(self, node):
            # Create settings section with documentation.
            setting_header = Statement.from_tokens([
                Token(Token.SETTING_HEADER, '*** Settings ***'),
                Token(Token.EOL, '\n')
            ])
            documentation = Statement.from_tokens([
                Token(Token.DOCUMENTATION, 'Documentation'),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'This is getting pretty advanced'),
                Token(Token.EOL, '\n'),
                Token(Token.CONTINUATION, '...'),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'and this API definitely could be better.'),
                Token(Token.EOL, '\n')
            ])
            empty_line = Statement.from_tokens([
                Token(Token.EOL, '\n')
            ])
            body = [documentation, empty_line]
            settings = SettingSection(setting_header, body)
            # Add settings to the beginning of the file.
            node.sections.insert(0, settings)
            # Must call `generic_visit` to visit also child nodes.
            return self.generic_visit(node)


    model = get_model('example.robot')
    modifier = TestModifier()
    modifier.visit(model)
    model.save()

Executing model
---------------

It is possible to convert a parsed and possibly modified model into an
executable :class:`~robot.running.model.TestSuite` structure by using its
:func:`~robot.running.model.TestSuite.from_model` class method. In this case
the :func:`~.parser.parser.get_model` function should be given the ``curdir``
argument to get possible ``${CURDIR}`` variable resolved correctly.

::

     from robot.api import get_model, TestSuite

     model = get_model('example.robot', curdir='/home/robot/example')
     # modify model as needed
     suite = TestSuite.from_model(model)
     suite.run()

For more details about executing the created
:class:`~robot.running.model.TestSuite` object, see the documentation
of its :meth:`~robot.running.model.TestSuite.run` method. Notice also
that if you do not need to modify the parsed model, it is easier to
get the executable suite by using the
:func:`~robot.running.model.TestSuite.from_file_system` class method.
"""

from .lexer import get_tokens, get_resource_tokens, get_init_tokens, Token
from .model import ModelTransformer, ModelVisitor
from .parser import get_model, get_resource_model, get_init_model
from .suitestructure import SuiteStructureBuilder, SuiteStructureVisitor
