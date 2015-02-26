*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/module.py
Force Tags        regression    pybot    jybot
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
    Keyword Name Should Be     5    Set Name Using Robot Name Attribute

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     1    a1=d    *a2
    Keyword Arguments Should Be     5    a    b    *args    **kwargs

Keyword Documentation
    Keyword Doc Should Start With    0   Get the intialization variables
    Keyword Doc Should Be    1   A keyword\n\nSee `get hello` for details

Valid non-ASCII
    Keyword Doc Should Be    2    Hyvää yötä.\n\nСпасибо!
    Keyword Doc Should Be    4    Hyvää yötä.

Invalid non-ASCII
    ${path}    ${base} =    Split Path    ${INTERPRETER}
    ${expected} =   Set Variable If    'ipy' not in '${base}'
    ...    Hyv\\xe4\\xe4 y\\xf6t\\xe4.    Hyvää yötä.
    Keyword Doc Should Be    3    ${expected}
