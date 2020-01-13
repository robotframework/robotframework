*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/ExampleSpec.xml
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    Example

Documentation
    Doc Should Start With
    ...    Library for `libdoc.py` testing purposes.
    ...
    ...    This library is only used in an example and it doesn't do anything useful.

Version
    Version Should Match    1.0

Type
    Type Should Be    library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    global

Named Args
    Named Args Should Be    no

Init Documentation
    Init Doc Should Be    0   Creates new Example test library 1
    Init Doc Should Be    1   Creates new Example test library 2
    Init Doc Should Be    2   Creates new Example test library 3

Init Arguments
    Init Arguments Should Be    0
    Init Arguments Should Be    1    arg
    Init Arguments Should Be    2    i

Keyword Names
    Keyword Name Should Be    0    Keyword
    Keyword Name Should Be    1    My Keyword

Keyword Arguments
    Keyword Arguments Should Be   0    arg
    Keyword Arguments Should Be   1

Keyword Documentation
    Keyword Doc Should Be    0
    ...    Takes one `arg` and *does nothing* with it.
    ...
    ...    Example:
    ...    | Your Keyword | xxx |
    ...    | Your Keyword | yyy |
    ...
    ...    See `My Keyword` for no more information.
    Keyword Doc Should Be    1
    ...    Does nothing & <doc> has "stuff" to 'escape'!! and ignored indentation
    ...    Tags: in spec these wont become tags

Keyword Tags
    Keyword Tags Should Be    0    tag1    tag2
    Keyword Tags Should Be    1
    Keyword Tags Should Be    2

Non ASCII
    Keyword Doc Should Be    2    Hyvää yötä.\n\nСпасибо!
