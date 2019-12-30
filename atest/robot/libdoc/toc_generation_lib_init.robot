*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/TocLibraryInitRobot.py

Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                  TocLibraryInitRobot

Documentation
    Doc Should Be
    ...    Simple library
    ...
    ...    == Table of contents ==
    ...
    ...    - `1 Heading`
    ...    - `2 Heading`
    ...    - `Importing`
    ...    - `Shortcuts`
    ...    - `Keywords`
    ...
    ...    = 1 Heading =
    ...
    ...    Some text here for chapter 1.
    ...
    ...    = 2 Heading =
    ...
    ...    Second chapter text there.
    ...
    ...    Second paragraph.

Version
    Version Should Be               ${EMPTY}

Type
    Type Should Be                  library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                 test case

Named Args
    Named Args Should Be            yes

Library Has Init
    Init Doc Should Be              0    This library has init.

Keyword Names
    Keyword Name Should Be          0    My Keyword

Keyword Arguments
    Keyword Arguments Should Be     0

Keyword Documentation
    Keyword Doc Should Be           0    Keyword documentation

Keyword tags
    Keyword Tags Should Be          0

