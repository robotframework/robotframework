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

r"""Public API for parsing, inspecting and modifying test data.

Exposed API
-----------

The publicly exposed parsing entry points are the following:

* :func:`~.lexer.lexer.get_tokens`,
  :func:`~.lexer.lexer.get_resource_tokens`, and
  :func:`~.lexer.lexer.get_init_tokens`
  functions for `parsing data to tokens`_.

* :class:`~.lexer.tokens.Token` class that contains all token types as
  class attributes.

* :func:`~.parser.parser.get_model`,
  :func:`~.parser.parser.get_resource_model`, and
  :func:`~.parser.parser.get_init_model`
  functions for `parsing data to model`_ represented as
  an abstract syntax tree (AST).

* `Model objects`_ used by the AST model.

* :class:`~robot.parsing.model.visitor.ModelVisitor`
  to ease `inspecting model`_ and `modifying data`_.

* :class:`~robot.parsing.model.visitor.ModelTransformer`
  for `adding and removing nodes`_.

.. note:: This module is new in Robot Framework 4.0. In Robot Framework 3.2 functions
          for getting tokens and model as well as the :class:`~.lexer.tokens.Token`
          class were exposed directly via the :mod:`robot.api` package, but other
          parts of the parsing API were not publicly exposed. All code targeting
          Robot Framework 4.0 or newer should use this module because parsing related
          functions and classes will be removed from :mod:`robot.api` in the future.

.. note:: Parsing was totally rewritten in Robot Framework 3.2 and external
          tools using the parsing APIs need to be updated. Depending on
          the use case, it may be possible to use the higher level
          :func:`~robot.running.builder.builders.TestSuiteBuilder` instead.

Parsing data to tokens
----------------------

Data can be parsed to tokens by using
:func:`~.lexer.lexer.get_tokens`,
:func:`~.lexer.lexer.get_resource_tokens` or
:func:`~.lexer.lexer.get_init_tokens` functions depending on whether the data
represent a test case (or task) file, a resource file, or a suite
initialization file. In practice the difference between these functions is
what settings and sections are valid.

Typically the data is easier to inspect and modify by using the higher level
model discussed in the next section, but in some cases having just the tokens
can be enough. Tokens returned by the aforementioned functions are
:class:`~.lexer.tokens.Token` instances and they have the token type, value,
and position easily available as their attributes. Tokens also have useful
string representation used by the example below::

    from robot.api.parsing import get_tokens

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

The output shows the token type, value, line number and column offset. When finding
tokens by their type, the constants in the :class:`~.lexer.tokens.Token` class such
as ``Token.TESTCASE_NAME`` and ``Token.EOL`` should be used instead the values
of these constants like ``'TESTCASE NAME'`` and ``'EOL'``. These values have
changed slightly in Robot Framework 4.0 and they may change in the future as well.

The ``EOL`` tokens denote end of a line and they include the newline character
and possible trailing spaces. The ``EOS`` tokens denote end of a logical
statement. Typically a single line forms a statement, but when the ``...``
syntax is used for continuation, a statement spans multiple lines. In
special cases a single line can also contain multiple statements.

Errors caused by unrecognized data such as non-existing section or setting names
are handled during the tokenizing phase. Such errors are reported using tokens
that have ``ERROR`` type and the actual error message in their ``error`` attribute.
Syntax errors such as empty FOR loops are only handled when building the higher
level model discussed below.

See the documentation of :func:`~.lexer.lexer.get_tokens` for details
about different ways how to specify the data to be parsed, how to control
should all tokens or only data tokens be returned, and should variables in
keyword arguments and elsewhere be tokenized or not.

Parsing data to model
---------------------

Data can be parsed to a higher level model by using
:func:`~.parser.parser.get_model`,
:func:`~.parser.parser.get_resource_model`, or
:func:`~.parser.parser.get_init_model` functions depending on the type of
the parsed file same way as when `parsing data to tokens`_.

The model is represented as an abstract syntax tree (AST) implemented on top
of Python's standard `ast.AST`_ class. To see how the model looks like, it is
possible to use the `ast.dump()`_ function or the third-party astpretty_
module::

    import ast
    import astpretty
    from robot.api.parsing import get_model

    model = get_model('example.robot')
    print(ast.dump(model, include_attributes=True))
    print('-' * 72)
    astpretty.pprint(model)

Running this code with the :file:`example.robot` file from the previous
section would produce so much output that it is not included here. If
you are going to work with Robot Framework's AST, you are recommended to
try that on your own.

.. _ast: https://docs.python.org/library/ast.html
.. _ast.AST: https://docs.python.org/library/ast.html#ast.AST
.. _ast.NodeVisitor: https://docs.python.org/library/ast.html#ast.NodeVisitor
.. _ast.NodeTransformer: https://docs.python.org/library/ast.html#ast.NodeTransformer
.. _ast.dump(): https://docs.python.org/library/ast.html#ast.dump
.. _astpretty: https://pypi.org/project/astpretty

Model objects
-------------

The model is build from nodes that are based `ast.AST`_ and further categorized
to blocks and statements. Blocks can contain other blocks and statements as
child nodes whereas statements only have tokens containing the actual data as
:class:`~.lexer.tokens.Token` instances. Both statements and blocks expose
their position information via ``lineno``, ``col_offset``, ``end_lineno`` and
``end_col_offset`` attributes and some nodes have also other special attributes
available.

Blocks:

- :class:`~robot.parsing.model.blocks.File` (the root of the model)
- :class:`~robot.parsing.model.blocks.SettingSection`
- :class:`~robot.parsing.model.blocks.VariableSection`
- :class:`~robot.parsing.model.blocks.TestCaseSection`
- :class:`~robot.parsing.model.blocks.KeywordSection`
- :class:`~robot.parsing.model.blocks.CommentSection`
- :class:`~robot.parsing.model.blocks.TestCase`
- :class:`~robot.parsing.model.blocks.Keyword`
- :class:`~robot.parsing.model.blocks.For`
- :class:`~robot.parsing.model.blocks.If`

Statements:

- :class:`~robot.parsing.model.statements.SectionHeader`
- :class:`~robot.parsing.model.statements.LibraryImport`
- :class:`~robot.parsing.model.statements.ResourceImport`
- :class:`~robot.parsing.model.statements.VariablesImport`
- :class:`~robot.parsing.model.statements.Documentation`
- :class:`~robot.parsing.model.statements.Metadata`
- :class:`~robot.parsing.model.statements.ForceTags`
- :class:`~robot.parsing.model.statements.DefaultTags`
- :class:`~robot.parsing.model.statements.SuiteSetup`
- :class:`~robot.parsing.model.statements.SuiteTeardown`
- :class:`~robot.parsing.model.statements.TestSetup`
- :class:`~robot.parsing.model.statements.TestTeardown`
- :class:`~robot.parsing.model.statements.TestTemplate`
- :class:`~robot.parsing.model.statements.TestTimeout`
- :class:`~robot.parsing.model.statements.Variable`
- :class:`~robot.parsing.model.statements.TestCaseName`
- :class:`~robot.parsing.model.statements.KeywordName`
- :class:`~robot.parsing.model.statements.Setup`
- :class:`~robot.parsing.model.statements.Teardown`
- :class:`~robot.parsing.model.statements.Tags`
- :class:`~robot.parsing.model.statements.Template`
- :class:`~robot.parsing.model.statements.Timeout`
- :class:`~robot.parsing.model.statements.Arguments`
- :class:`~robot.parsing.model.statements.Return`
- :class:`~robot.parsing.model.statements.KeywordCall`
- :class:`~robot.parsing.model.statements.TemplateArguments`
- :class:`~robot.parsing.model.statements.ForHeader`
- :class:`~robot.parsing.model.statements.IfHeader`
- :class:`~robot.parsing.model.statements.ElseIfHeader`
- :class:`~robot.parsing.model.statements.ElseHeader`
- :class:`~robot.parsing.model.statements.End`
- :class:`~robot.parsing.model.statements.Comment`
- :class:`~robot.parsing.model.statements.Error`
- :class:`~robot.parsing.model.statements.EmptyLine`

Inspecting model
----------------

The easiest way to inspect what data a model contains is implementing
:class:`~robot.parsing.model.visitor.ModelVisitor` and creating
``visit_NodeName`` to visit nodes with name ``NodeName`` as needed.
The following example illustrates how to find what tests a certain test
case file contains::

    from robot.api.parsing import get_model, ModelVisitor


    class TestNamePrinter(ModelVisitor):

        def visit_File(self, node):
            print(f"File '{node.source}' has following tests:")
            # Call `generic_visit` to visit also child nodes.
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

Handling errors in model
------------------------

All nodes in the model have ``errors`` attribute that contains possible errors
the node has. These errors include syntax errors such as empty FOR loops or IF
without a condition as well as errors caused by unrecognized data such as
non-existing section or setting names.

Unrecognized data is handled already during the tokenizing__ phase. In the model
such data is represented as :class:`~robot.parsing.model.statements.Error`
nodes and their ``errors`` attribute contain error information got from the
underlying ``ERROR`` tokens. Syntax errors do not create
:class:`~robot.parsing.model.statements.Error`
nodes, but instead the model has normal nodes such as
:class:`~robot.parsing.model.blocks.If`
with errors in their ``errors`` attribute.

A simple way to go through the model and see are there errors is using the
:class:`~robot.parsing.model.visitor.ModelVisitor`
discussed in the previous section::

    class ErrorReporter(ModelVisitor):

        # Implement `generic_visit` to visit all nodes.
        def generic_visit(self, node):
            if node.errors:
                print(f'Error on line {node.lineno}:')
                for error in node.errors:
                    print(f'- {error}')
            ModelVisitor.generic_visit(self, node)

__ `Parsing data to tokens`_

Modifying data
--------------

Existing data the model contains can be modified simply by modifying values of
the underlying tokens. If changes need to be saved, that is as easy as calling
the :meth:`~.model.blocks.File.save` method of the root model object. When
just modifying token values, it is possible to still use
:class:`~robot.parsing.model.visitor.ModelVisitor`
discussed in the above section. The next section discusses adding or removing
nodes and then
:class:`~robot.parsing.model.visitor.ModelTransformer`
should be used instead.

Modifications to tokens obviously require finding the tokens to be modified.
The first step is finding nodes containing the tokens by implementing
needed ``visit_NodeName`` methods. Then the exact token or tokens
can be found using nodes'
:meth:`~.model.statements.Statement.get_token` or
:meth:`~.model.statements.Statement.get_tokens` methods.
If only token values are needed,
:meth:`~.model.statements.Statement.get_value` or
:meth:`~.model.statements.Statement.get_values` can be used as a shortcut.
First finding nodes and then the right tokens is illustrated by
this keyword renaming example::

    from robot.api.parsing import get_model, ModelVisitor, Token


    class KeywordRenamer(ModelVisitor):

        def __init__(self, old_name, new_name):
            self.old_name = self.normalize(old_name)
            self.new_name = new_name

        def normalize(self, name):
            return name.lower().replace(' ', '').replace('_', '')

        def visit_KeywordName(self, node):
            '''Rename keyword definitions.'''
            if self.normalize(node.name) == self.old_name:
                token = node.get_token(Token.KEYWORD_NAME)
                token.value = self.new_name

        def visit_KeywordCall(self, node):
            '''Rename keyword usages.'''
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

Bigger changes to the model are somewhat more complicated than just modifying
existing token values. When doing this kind of changes,
:class:`~robot.parsing.model.visitor.ModelTransformer`
should be used instead of
:class:`~robot.parsing.model.visitor.ModelVisitor`
that was discussed in the previous sections.

Removing nodes is relative easy and is accomplished by returning ``None``
from ``visit_NodeName`` methods. Remember to return the original node,
or possibly a replacement node, from all of these methods when you do not
want a node to be removed.

Adding nodes requires constructing needed `Model objects`_ and adding them
to the model. The following example demonstrates both removing and adding nodes.
If you run it against the earlier :file:`example.robot`, you see that
the first test gets a new keyword, the second test is removed, and
settings section with documentation is added.

::

    from robot.api.parsing import (
        get_model, Documentation, EmptyLine, KeywordCall,
        ModelTransformer, SettingSection, SectionHeader, Token
    )


    class TestModifier(ModelTransformer):

        def visit_TestCase(self, node):
            # The matched `TestCase` node is a block with `header` and
            # `body` attributes. `header` is a statement with familiar
            # `get_token` and `get_value` methods for getting certain
            # tokens or their value.
            name = node.header.get_value(Token.TESTCASE_NAME)
            # Returning `None` drops the node altogether i.e. removes
            # this test.
            if name == 'Second example':
                return None
            # Construct new keyword call statement from tokens. See `visit_File`
            # below for an example creating statements using `from_params`.
            new_keyword = KeywordCall([
                Token(Token.SEPARATOR, '    '),
                Token(Token.KEYWORD, 'New Keyword'),
                Token(Token.SEPARATOR, '    '),
                Token(Token.ARGUMENT, 'xxx'),
                Token(Token.EOL)
            ])
            # Add the keyword call to test as the second item.
            node.body.insert(1, new_keyword)
            # No need to call `generic_visit` because we are not
            # modifying child nodes. The node itself must to be
            # returned to avoid dropping it.
            return node

        def visit_File(self, node):
            # Create settings section with documentation. Needed header and body
            # statements are created using `from_params` method. This is typically
            # more convenient than creating statements based on tokens like above.
            settings = SettingSection(
                header=SectionHeader.from_params(Token.SETTING_HEADER),
                body=[
                    Documentation.from_params('This is a really\npowerful API!'),
                    EmptyLine.from_params()
                ]
            )
            # Add settings to the beginning of the file.
            node.sections.insert(0, settings)
            # Call `generic_visit` to visit also child nodes.
            return self.generic_visit(node)


    model = get_model('example.robot')
    TestModifier().visit(model)
    model.save('modified.robot')

Executing model
---------------

It is possible to convert a parsed and possibly modified model into an
executable :class:`~robot.running.model.TestSuite` structure by using its
:func:`~robot.running.model.TestSuite.from_model` class method. In this case
the :func:`~.parser.parser.get_model` function should be given the ``curdir``
argument to get possible ``${CURDIR}`` variable resolved correctly.

::

     from robot.api import TestSuite
     from robot.api.parsing import get_model

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

from robot.parsing import (
    get_tokens,
    get_resource_tokens,
    get_init_tokens,
    get_model,
    get_resource_model,
    get_init_model,
    Token
)
from robot.parsing.model.blocks import (
    File,
    SettingSection,
    VariableSection,
    TestCaseSection,
    KeywordSection,
    CommentSection,
    TestCase,
    Keyword,
    For,
    If
)
from robot.parsing.model.statements import (
    SectionHeader,
    LibraryImport,
    ResourceImport,
    VariablesImport,
    Documentation,
    Metadata,
    ForceTags,
    DefaultTags,
    SuiteSetup,
    SuiteTeardown,
    TestSetup,
    TestTeardown,
    TestTemplate,
    TestTimeout,
    Variable,
    TestCaseName,
    KeywordName,
    Setup,
    Teardown,
    Tags,
    Template,
    Timeout,
    Arguments,
    Return,
    KeywordCall,
    TemplateArguments,
    ForHeader,
    IfHeader,
    ElseIfHeader,
    ElseHeader,
    End,
    Comment,
    Error,
    EmptyLine
)
from robot.parsing.model.visitor import (
    ModelTransformer,
    ModelVisitor
)
