*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/./Example.java
Force Tags        require-jython    require-tools.jar
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                   Example

Documentation
    Doc Should Start With
    ...    Library for `libdoc.py` testing purposes.
    ...
    ...    This library is only used in an example and it doesn't do anything useful.

Version
    Version Should Be                1.0 <alpha>

Type
    Type Should Be                   LIBRARY

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                  GLOBAL

Source Info
    Source Should Be                 ${TESTDATADIR}/Example.java
    Lineno Should Be                 ${None}

Spec version
    Spec version should be correct

Library Tags
    Specfile Tags Should Be          bar    foo

Init Documentation
    Init Doc Should Start With       0    Creates new Example test library 1
    Init Doc Should Start With       1    Creates new Example test library 2
    Init Doc Should Start With       2    Creates new Example test library 3

Init Arguments
    Init Arguments Should Be         0
    Init Arguments Should Be         1    arg    /
    Init Arguments Should Be         2    i    /

Keyword Names
    Keyword Name Should Be           1    Keyword
    Keyword Name Should Be           5    My Keyword

Keyword Arguments
    Keyword Arguments Should Be      1    arg    /
    Keyword Arguments Should Be      5
    Keyword Arguments Should Be     -4    *varargs
    Keyword Arguments Should Be     -3    normal   /     *varargs

Keyword Documentation
    Keyword Doc Should Start With    1
    ...    Takes one `arg` and *does nothing* with it.
    ...
    ...    Example:
    ...    | Your Keyword | xxx |
    ...    | Your Keyword | yyy |
    ...
    ...    See `My Keyword` for no more information.
    Keyword Doc Should Start With    5
    ...    Does nothing & <doc> has "stuff" to 'escape'!!
    ...    ${SPACE * 4}We also got some
    ...    ${SPACE * 8}indentation
    ...    ${SPACE * 8}here.
    ...    Back in the normal indentation level.

Deprecation
    Keyword Doc Should Be            0    *DEPRECATED!?!?!!*
    Keyword Should Be Deprecated     0

Non ASCII
    Keyword Doc Should Be            6    Hyvää yötä.\n\nСпасибо!

Lists as varargs
    Keyword Arguments Should Be     -1    *varargsList

Kwargs
    Keyword Arguments Should Be      2    normal    /    *varargs    **kwargs

Only last map is kwargs
    Keyword Arguments Should Be      3    normal    /    **kwargs

Only last list is varargs
    Keyword Arguments Should Be     -2    normalArray    /    *varargs

Last argument overrides
    Keyword Arguments Should Be      4    normalArray    normalMap    normal    /

Keyword tags
    Keyword Tags Should Be           5    bar    foo

No keyword source info
    Keyword Should Not Have Source   0
    Keyword Should Not Have Lineno   0

Private constructors are ignored
    Keyword Count Should Be          3    type=inits/init

Private keywords are ignored
    Keyword Count Should Be         11
