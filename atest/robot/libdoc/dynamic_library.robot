*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DynamicLibrary.py::required
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be                   DynamicLibrary

Documentation
    Doc Should Start With            Dummy documentation for `__intro__`.

Version
    Version Should Match             0.1

Type
    Type Should Be                   LIBRARY

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                  TEST

Source info
    Source should be                 ${TESTDATADIR}/DynamicLibrary.py
    Lineno should be                 5

Spec version
    Spec version should be correct

Library Tags
    Specfile Tags Should Be          hyvää    my    tägs    yötä

Init documentation
    Init Doc Should Start With       0     Dummy documentation for `__init__`.

Init arguments
    Init Arguments Should Be         0     arg1    arg2=These args are shown in docs

Init Source Info
    Keyword Should Not Have Source   0     xpath=inits/init
    Keyword Lineno Should Be         0     9      xpath=inits/init

Keyword names
    Keyword Name Should Be           0     0
    Keyword Name Should Be           5     Keyword 1
    Keyword Name Should Be           7     KW 2

Keyword arguments
    Keyword Arguments Should Be      0
    Keyword Arguments Should Be      5     arg1
    Keyword Arguments Should Be      7     arg1    arg2

Default values
    Keyword Arguments Should Be      1     old=style    new=style    cool=True

Keyword-only arguments
    Keyword Arguments Should Be      6     *    kwo    another=default
    Keyword Arguments Should Be      8     *varargs    a    b=2    c    **kws

Embedded arguments
    Keyword Name Should Be           2     Em\${bed}ed \${args} 2
    Keyword Name Should Be           3     Embedded \${args} 1
    Keyword Arguments Should Be      2
    Keyword Arguments Should Be      3

Keyword documentation
    Keyword Doc Should Start With    0     Dummy documentation for `0`.
    Keyword Doc Should Start With    5     Dummy documentation for `Keyword 1`.
    Keyword Doc Should Start With    7     Dummy documentation for `KW2`.

Non-ASCII Unicode
    Keyword Name Should Be           12    Nön-äscii Ünicöde
    Keyword Doc Should Be            12    Hyvää yötä.\n\nСпасибо! (Unicode)

Non-ASCII UTF-8
    Keyword Name Should Be           13    Nön-äscii ÜTF-8
    Keyword Doc Should Be            13    Hyvää yötä.\n\nСпасибо! (UTF-8)

No argspec
    Keyword Arguments Should be      9     *varargs   **kwargs

Keyword tags
    Keyword Tags Should Be           17    my    tägs

Keyword tags from documentation
    Keyword Tags Should Be           12    hyvää   yötä
    Keyword Tags Should Be           13    hyvää   yötä

Keyword types
    Keyword Arguments Should Be      18    integer: int    no type    boolean: bool = True

No keyword source info
    Keyword Name Should Be           0     0
    Keyword Should Not Have Source   0
    Keyword Should Not Have Lineno   0

Keyword source info
    Keyword Name Should Be           14    Source Info
    Keyword Should Not Have Source   14
    Keyword Lineno Should Be         14    83

Keyword source info with different path than library
    Keyword Name Should Be           16    Source Path Only
    Keyword Source Should Be         16    ${TESTDATADIR}/Annotations.py
    Keyword Should Not Have Lineno   16

Keyword source info with lineno only
    Keyword Name Should Be           15    Source Lineno Only
    Keyword Should Not Have Source   15
    Keyword Lineno Should Be         15    12345

Non-existing source info
    Keyword Name Should Be           10    Non-existing Source Path And Lineno
    Keyword Source Should Be         10    whatever:xxx
    Keyword Should Not Have Lineno   10
    Keyword Name Should Be           11    Non-existing Source Path With Lineno
    Keyword Source Should Be         11    everwhat
    Keyword Lineno Should Be         11    42

Invalid source info
    ${error} =    Catenate
    ...    [ ERROR ] Error in library 'DynamicLibrary':
    ...    Getting source information for keyword 'Invalid Source Info' failed:
    ...    Calling dynamic method 'get_keyword_source' failed:
    ...    Return value must be a string, got integer.
    Should Start With    ${OUTPUT}    ${error}
