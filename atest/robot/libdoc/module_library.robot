*** Settings ***
Suite Setup        Run Libdoc And Parse Output    ${TESTDATADIR}/module.py
Resource           libdoc_resource.robot

*** Variables ***
${PY3 or IPY}      ${{$INTERPRETER.is_py3 or $INTERPRETER.is_ironpython}}

*** Test Cases ***
Name
    Name Should Be                   module

Documentation
    Doc Should Be                    Module test library.

Version
    Version Should Be                0.1-alpha

Type
    Type Should Be                   LIBRARY

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                  GLOBAL

Source info
    Source should be                 ${TESTDATADIR}/module.py
    Lineno should be                 1

Spec version
    Spec version should be correct

Has No Inits
    Should Have No Init

Keyword Names
    Keyword Name Should Be           0     Get Hello
    Keyword Name Should Be           1     Keyword
    Keyword Name Should Be           14    Set Name Using Robot Name Attribute

Keyword Arguments
    Keyword Arguments Should Be      0
    Keyword Arguments Should Be      1     a1=d    *a2
    Keyword Arguments Should Be      12    a=1    b=True    c=(1, 2, None)
    Keyword Arguments Should Be      13    arg=\\ robot \\ escapers\\n\\t\\r \\ \\
    Keyword Arguments Should Be      14    a    b    *args    **kwargs

Non-ASCII Unicode Defaults
    Keyword Arguments Should Be      10    arg=hyvä

Non-ASCII Bytes Defaults
    Keyword Arguments Should Be      6     arg=hyv\\xe4

Non-ASCII String Defaults
    Keyword Arguments Should Be      7     arg=${{'hyvä' if $PY3_or_IPY else 'hyv\\xc3\\xa4'}}

Embedded Arguments
    Keyword Name Should Be           15    Takes \${embedded} \${args}
    Keyword Arguments Should Be      15

Keyword Documentation
    Keyword Doc Should Be            1     A keyword.\n\nSee `get hello` for details.
    Keyword Doc Should Be            0     Get hello.\n\nSee `importing` for explanation of nothing\nand `introduction` for no more information.
    Keyword Doc Should Be            4     Set tags in documentation.

Multiline Documentation With Split Short Doc
    ${doc} =    Catenate    SEPARATOR=\n
    ...    This is short doc.
    ...    It can span multiple
    ...    physical
    ...    lines.
    ...    ${EMPTY}
    ...    This is body. It can naturally also
    ...    contain multiple lines.
    ...    ${EMPTY}
    ...    And paragraphs.
    Keyword Doc Should Be            5     ${doc}

Non-ASCII Unicode doc
    Keyword Doc Should Be            11    Hyvää yötä.\n\nСпасибо!

Non-ASCII string doc
    Keyword Doc Should Be            8     Hyvää yötä.

Non-ASCII string doc with escapes
    Keyword Doc Should Be            9     ${{'Hyvää yötä.' if $PY3_or_IPY else 'Hyv\\xe4\\xe4 y\\xf6t\\xe4.'}}

Keyword tags
    Keyword Tags Should Be           1
    Keyword Tags Should Be           2     1    one    yksi
    Keyword Tags Should Be           3     2    kaksi    two
    Keyword Tags Should Be           4     tag1    tag2

Keyword source info
    Keyword Name Should Be           0     Get Hello
    Keyword Should Not Have Source   0
    Keyword Lineno Should Be         0     19

Keyword source info with decorated function
    Keyword Name Should Be           15    Takes \${embedded} \${args}
    Keyword Should Not Have Source   15
    Keyword Lineno Should Be         15    81
