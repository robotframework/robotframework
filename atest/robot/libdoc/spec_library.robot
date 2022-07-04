*** Settings ***
Library           OperatingSystem
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/ExampleSpec.xml
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                 Example

Documentation
    Doc Should Start With
    ...    Library for `libdoc.py` testing purposes.
    ...
    ...    This library is only used in an example and it doesn't do anything useful.

Version
    Version Should Be              42

Type
    Type Should Be                 LIBRARY

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                GLOBAL

Source info
    Source should be               Example.py
    Lineno should be               8

Spec version
    Spec version should be correct

Library Tags
    Specfile Tags Should Be          tag1    tag2

Init Documentation
    Init Doc Should Be             0    Creates new Example test library 1
    Init Doc Should Be             1    Creates new Example test library 2
    Init Doc Should Be             2    Creates new Example test library 3

Init Arguments
    Init Arguments Should Be       0
    Init Arguments Should Be       1    arg
    Init Arguments Should Be       2    i

Init Source Info
    Keyword Should Not Have Source    0    xpath=inits/init
    Keyword Lineno Should Be          0    12      xpath=inits/init
    Keyword Should Not Have Source    1    xpath=inits/init
    Keyword Should Not Have Lineno    1    xpath=inits/init

Keyword Names
    Keyword Name Should Be         0    Keyword
    Keyword Name Should Be         1    My Keyword
    Keyword Name Should Be         2    Non Ascii Doc

Keyword Arguments
    Keyword Arguments Should Be    0    arg
    Keyword Arguments Should Be    1
    Keyword Arguments Should Be    2

Keyword Documentation
    Keyword Doc Should Be          0
    ...    Takes one `arg` and *does nothing* with it.
    ...
    ...    Example:
    ...    | Your Keyword | xxx |
    ...    | Your Keyword | yyy |
    ...
    ...    See `My Keyword` for no more information.
    Keyword Short Doc Should be    0    Takes one `arg` and *does nothing* with it.
    Keyword Doc Should Be          1
    ...    Does nothing & <doc> has "stuff" to 'escape'!! and ignored indentation
    ...    Tags: in spec these wont become tags
    Keyword Short Doc Should be    1
    ...    Does nothing & <doc> has "stuff" to 'escape'!! and ignored indentation Tags: in spec these wont become tags

Non ASCII
    Keyword Doc Should Be          2    Hyvää yötä.\n\nСпасибо!
    Keyword Shortdoc Should Be     2    Hyvää yötä.

Keyword Tags
    Keyword Tags Should Be         0    tag1    tag2
    Keyword Tags Should Be         1
    Keyword Tags Should Be         2

Private Keywords
    Keyword Should Not Be Private       0
    Keyword Should Be Private           1
    Keyword Should Not Be Private       2

Keyword Deprecation
    Keyword Should Not Be Deprecated    0
    Keyword Should Be Deprecated        1
    Keyword Should Not Be Deprecated    2

Keyword Source Info
    Keyword Should Not Have Source    0
    Keyword Should Not Have Lineno    0
    Keyword Should Not Have Source    1
    Keyword Lineno Should Be          1    42
    Keyword Source Should Be          2    Different!
    Keyword Lineno Should Be          2    666

'*.libspec' extension
    Copy File    ${TESTDATADIR}/ExampleSpec.xml    %{TEMPDIR}/Example.libspec
    Run Libdoc And Parse Output    %{TEMPDIR}/Example.libspec
    Test Everything

SOURCE_DATE_EPOCH is honored in Libdoc output
    [Setup]    Set Environment Variable    SOURCE_DATE_EPOCH    0
    Copy File    ${TESTDATADIR}/ExampleSpec.xml    %{TEMPDIR}/Example.libspec
    Run Libdoc And Parse Output    %{TEMPDIR}/Example.libspec
    Generated Should Be    1970-01-01T00:00:00+00:00
    [Teardown]    Remove Environment Variable    SOURCE_DATE_EPOCH

*** Keywords ***
Test Everything
    Name Should Be                    Example
    Doc Should Start With             Library for `libdoc.py` testing purposes.
    Version Should Be                 42
    Type Should Be                    LIBRARY
    Generated Should Be Defined
    Scope Should Be                   GLOBAL
    Source should be                  Example.py
    Lineno should be                  8
    Init Doc Should Be                0    Creates new Example test library 1
    Init Doc Should Be                1    Creates new Example test library 2
    Init Doc Should Be                2    Creates new Example test library 3
    Init Arguments Should Be          0
    Init Arguments Should Be          1    arg
    Init Arguments Should Be          2    i
    Keyword Should Not Have Source    0    xpath=inits/init
    Keyword Lineno Should Be          0    12      xpath=inits/init
    Keyword Should Not Have Source    1    xpath=inits/init
    Keyword Should Not Have Lineno    1    xpath=inits/init
    Keyword Name Should Be            0    Keyword
    Keyword Name Should Be            1    My Keyword
    Keyword Name Should Be            2    Non Ascii Doc
    Keyword Arguments Should Be       0    arg
    Keyword Arguments Should Be       1
    Keyword Arguments Should Be       2
    Keyword Doc Should Start With     0    Takes one `arg` and *does nothing* with it.
    Keyword Doc Should Start With     1    Does nothing & <doc> has "stuff" to 'escape'!! and ignored indentation
    Keyword Doc Should Be             2    Hyvää yötä.\n\nСпасибо!
    Keyword Tags Should Be            0    tag1    tag2
    Keyword Tags Should Be            1
    Keyword Tags Should Be            2
    Keyword Should Not Be Private     0
    Keyword Should Be Private         1
    Keyword Should Not Be Private     2
    Keyword Should Not Be Deprecated  0
    Keyword Should Be Deprecated      1
    Keyword Should Not Be Deprecated  2
    Keyword Should Not Have Source    0
    Keyword Should Not Have Lineno    0
    Keyword Should Not Have Source    1
    Keyword Lineno Should Be          1    42
    Keyword Source Should Be          2    Different!
    Keyword Lineno Should Be          2    666
