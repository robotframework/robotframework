*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DynamicLibrary.py::required
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    DynamicLibrary

Documentation
    Doc Should Start With    Dummy documentation for `__intro__`.

Version
    Version Should Match    0.1

Type
    Type Should Be    library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    test case

Named Args
    Named Args Should Be    yes

Init Documentation
    Init Doc Should Start With    0   Dummy documentation for `__init__`.

Init Arguments
    Init Arguments Should Be    0    arg1    arg2=This is shown in docs

Keyword Names
    Keyword Name Should Be     0    0
    Keyword Name Should Be     3    Keyword 1
    Keyword Name Should Be     4    KW 2

Keyword Arguments
    Keyword Arguments Should Be     0
    Keyword Arguments Should Be     3    arg1
    Keyword Arguments Should Be     4    arg1    arg2

Embedded Arguments
    Keyword Name Should Be     1    Em\${bed}ed \${args} 2
    Keyword Name Should Be     2    Embedded \${args} 1
    Keyword Arguments Should Be     1
    Keyword Arguments Should Be     2

Keyword Documentation
    Keyword Doc Should Start With    0   Dummy documentation for `0`.
    Keyword Doc Should Start With    3   Dummy documentation for `Keyword 1`.
    Keyword Doc Should Start With    4   Dummy documentation for `KW2`.

Non-ASCII Unicode
    Keyword Name Should Be    6    Nön-äscii Ünicöde
    Keyword Doc Should Be     6    Hyvää yötä.\n\nСпасибо! (Unicode)

Non-ASCII UTF-8
    Keyword Name Should Be    7    Nön-äscii ÜTF-8
    Keyword Doc Should Be     7    Hyvää yötä.\n\nСпасибо! (UTF-8)

No Argspec
    Keyword Arguments Should be     5     *varargs   **kwargs

Keyword Tags
    Keyword Tags Should Be    6    hyvää   yötä
    Keyword Tags Should Be    7    hyvää   yötä
