*** Settings ***
Documentation      Test that Libdoc can read old XML and JSON spec files.
Test Template      Generate and validate
Resource           libdoc_resource.robot

*** Variables ***
${BASE}            ${TESTDATADIR}/BackwardsCompatibility

*** Test Cases ***
Latest
    ${BASE}.py    source=${BASE}.py

RF 6.1 XML
    ${BASE}-6.1.xml

RF 6.1 JSON
    ${BASE}-6.1.json

RF 5.0 XML
    ${BASE}-5.0.xml

RF 5.0 JSON
    ${BASE}-5.0.json

RF 4.0 XML
    ${BASE}-4.0.xml    datatypes=True

RF 4.0 JSON
    ${BASE}-4.0.json    datatypes=True

*** Keywords ***
Generate and validate
    [Arguments]    ${path}    ${source}=BackwardsCompatibility.py    ${datatypes}=False
    # JSON source files must be generated using RAW format as well.
    Run Libdoc And Parse Output    --specdocformat RAW ${path}
    Validate    ${source}    ${datatypes}

Validate
    [Arguments]    ${source}    ${datatypes}=False
    [Tags]    robot:recursive-continue-on-failure
    Validate library    ${source}
    Validate keyword 'Simple'
    Validate keyword 'Arguments'
    Validate keyword 'Types'
    Validate keyword 'Special Types'
    Validate keyword 'Union'

Validate library
    [Arguments]    ${source}
    Name Should Be                     BackwardsCompatibility
    Version Should Be                  1.0
    Doc Should Start With              Library for testing backwards compatibility.\n
    Type Should Be                     LIBRARY
    Scope Should Be                    GLOBAL
    Format Should Be                   ROBOT
    Source Should Be                   ${source}
    Lineno Should Be                   1
    Generated Should Be Defined
    Spec Version Should Be Correct
    Should Have No Init
    Keyword Count Should Be            5

Validate keyword 'Simple'
    Keyword Name Should Be             1    Simple
    Keyword Doc Should Be              1    Some doc.
    Keyword Tags Should Be             1    example
    Keyword Lineno Should Be           1    34
    Keyword Arguments Should Be        1

Validate keyword 'Arguments'
    Keyword Name Should Be             0    Arguments
    Keyword Doc Should Be              0    ${EMPTY}
    Keyword Tags Should Be             0
    Keyword Lineno Should Be           0    42
    Keyword Arguments Should Be        0    a    b=2    *c    d=4    e    **f

Validate keyword 'Types'
    Keyword Name Should Be             3    Types
    Keyword Arguments Should Be        3    a: int    b: bool = True

Validate keyword 'Special Types'
    Keyword Name Should Be             2    Special Types
    Keyword Arguments Should Be        2    a: Color    b: Size

Validate keyword 'Union'
    Keyword Name Should Be             4    Union
    Keyword Arguments Should Be        4    a: int | float
