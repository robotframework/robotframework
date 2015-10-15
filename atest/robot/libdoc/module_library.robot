*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/module.py
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    module

Documentation
    Doc Should Be    Module test library.

Version
    Version Should Be    0.1-alpha

Type
    Type Should Be    library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    global

Named Args
    Named Args Should Be    yes

Has No Inits
    Should Have No Init

Keyword Names
    Keyword Name Should Be     0    Get Hello
    Keyword Name Should Be     1    Keyword
    Keyword Name Should Be     7    Set Name Using Robot Name Attribute

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     1    a1=d    *a2
    Keyword Arguments Should Be     7    a    b    *args    **kwargs

Embedded Arguments
    Keyword Name Should Be     8    Takes \${embedded} \${args}
    Keyword Arguments Should Be     8

Keyword Documentation
    Keyword Doc Should Start With    0   Get the intialization variables
    Keyword Doc Should Be    1   A keyword\n\nSee `get hello` for details

Valid non-ASCII
    Keyword Doc Should Be    4    Hyvää yötä.\n\nСпасибо!
    Keyword Doc Should Be    6    Hyvää yötä.

Invalid non-ASCII
    ${expected} =   Set Variable If    $INTERPRETER.is_py3 or $INTERPRETER.is_ironpython
    ...    Hyvää yötä.    Hyv\\xe4\\xe4 y\\xf6t\\xe4.
    Keyword Doc Should Be    5    ${expected}

Keyword tags
    Keyword Tags Should Be    1
    Keyword Tags Should Be    2    1    one    yksi
    Keyword Tags Should Be    3    2    kaksi    two
