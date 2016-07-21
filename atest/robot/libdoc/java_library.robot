*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/Example.java
Force Tags        require-jython    require-tools.jar
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    Example

Documentation
    Doc Should Start With
    ...    Library for `libdoc.py` testing purposes.\n\n
    ...    This library is only used in an example and it doesn't do anything useful.

Version
    Version Should Be    1.0 <alpha>

Type
    Type Should Be    library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    global

Named Args
    Named Args Should Be    no

Init Documentation
    Init Doc Should Start With    0   Creates new Example test library 1
    Init Doc Should Start With    1   Creates new Example test library 2
    Init Doc Should Start With    2   Creates new Example test library 3

Init Arguments
    Init Arguments Should Be    0
    Init Arguments Should Be    1    arg
    Init Arguments Should Be    2    i

Keyword Names
    Keyword Name Should Be    0    Keyword
    Keyword Name Should Be    4    My Keyword

Keyword Arguments
    Keyword Arguments Should Be     0    arg
    Keyword Arguments Should Be     4
    Keyword Arguments Should Be     -4    *varargs
    Keyword Arguments Should Be     -3    normal    *varargs

Keyword Documentation
    Keyword Doc Should Start With    0
    ...    Takes one `arg` and *does nothing* with it.\n\n
    ...    Example:\n
    ...    | Your Keyword | xxx |\n
    ...    | Your Keyword | yyy |\n\n
    ...    See `My Keyword` for no more information.
    Keyword Doc Should Start With    4
    ...    Does nothing & <doc> has "stuff" to 'escape'!!
    ...    \nand ignored indentation

Non ASCII
    Keyword Doc Should Be    5    Hyvää yötä.\n\nСпасибо!

Lists as varargs
    Keyword Arguments Should Be     -1    *varargsList

Kwargs
    Keyword Arguments Should Be     1    normal  *varargs  **kwargs

Only last map is kwargs
    Keyword Arguments Should Be     2    normal  **kwargs

Only last list is varargs
    Keyword Arguments Should Be     -2    normalArray  *varargs

Last argument overrides
    Keyword Arguments Should Be     3    normalArray  normalMap  normal

Keyword tags
    Keyword Tags Should Be    4    bar    foo
