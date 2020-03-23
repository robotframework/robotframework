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
    Type Should Be                   library

Generated
    Generated Should Be Defined

Scope
    Scope Should Be                  test case

Named args
    Named Args Should Be             yes

Init documentation
    Init Doc Should Start With       0     Dummy documentation for `__init__`.

Init arguments
    Init Arguments Should Be         0     arg1    arg2=This is shown in docs

Keyword names
    Keyword Name Should Be           0     0
    Keyword Name Should Be           4     Keyword 1
    Keyword Name Should Be           6     KW 2

Keyword arguments
    Keyword Arguments Should Be      0
    Keyword Arguments Should Be      4     arg1
    Keyword Arguments Should Be      6     arg1    arg2

Default values
    Keyword Arguments Should Be      1     old=style    new=style    cool=True

Keyword-only arguments
    Keyword Arguments Should Be      5     *    kwo    another=default
    Keyword Arguments Should Be      7     *varargs    a    b=2    c    **kws

Embedded arguments
    Keyword Name Should Be           2     Em\${bed}ed \${args} 2
    Keyword Name Should Be           3     Embedded \${args} 1
    Keyword Arguments Should Be      2
    Keyword Arguments Should Be      3

Keyword documentation
    Keyword Doc Should Start With    0     Dummy documentation for `0`.
    Keyword Doc Should Start With    4     Dummy documentation for `Keyword 1`.
    Keyword Doc Should Start With    6     Dummy documentation for `KW2`.

Non-ASCII Unicode
    Keyword Name Should Be           9     Nön-äscii Ünicöde
    Keyword Doc Should Be            9     Hyvää yötä.\n\nСпасибо! (Unicode)

Non-ASCII UTF-8
    Keyword Name Should Be           10    Nön-äscii ÜTF-8
    Keyword Doc Should Be            10    Hyvää yötä.\n\nСпасибо! (UTF-8)

No argspec
    Keyword Arguments Should be      8     *varargs   **kwargs

Keyword tags
    Keyword Tags Should Be           11    my    tägs

Keyword tags from documentation
    Keyword Tags Should Be           9     hyvää   yötä
    Keyword Tags Should Be           10    hyvää   yötä

Keyword types
    Keyword Arguments Should Be      12    integer: int    no type    boolean: bool=True
