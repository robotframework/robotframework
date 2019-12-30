*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/toc_resource.robot

Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                  toc_resource

Documentation
    Doc Should Be
    ...    Some documentation
    ...
    ...    == Table of contents ==
    ...
    ...    - `1 Heading`
    ...    - `2 Heading`
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
    Type Should Be                  resource

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                 ${EMPTY}

Named Args
    Named Args Should Be            yes

Library Has No Init
    Should Have No Init

Keyword Names
    Keyword Name Should Be          0    Other Keyword

Keyword Arguments
    Keyword Arguments Should Be     0

Keyword Documentation
    Keyword Doc Should Be           0    Some other documentation

Keyword tags
    Keyword Tags Should Be          0
