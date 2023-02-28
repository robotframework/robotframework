*** Settings ***
Documentation      Test that Libdoc can read old XML and JSON spec files.
Test Template      Generate and validate
Resource           libdoc_resource.robot

*** Variables ***
${BASE}            ${TESTDATADIR}/BackwardsCompatibility

*** Test Cases ***
Latest
    ${BASE}.py

RF 6.1 XML
    ${BASE}-6.1.xml

RF 6.1 JSON
    ${BASE}-6.1.json

RF 5.0 XML
    ${BASE}-5.0.xml

RF 5.0 JSON
    ${BASE}-5.0.json

RF 4.0 XML
    ${BASE}-4.0.xml    legacy=True

RF 4.0 JSON
    ${BASE}-4.0.json    legacy=True

*** Keywords ***
Generate and validate
    [Arguments]    ${source}    ${legacy}=False
    # JSON source files must be generated using RAW format as well.
    Run Libdoc And Parse Output    --specdocformat RAW ${source}
    Validate    ${legacy}    ${source.endswith('.xml')}

Validate
    [Arguments]    ${legacy}=False    ${xml}=True
    [Tags]    robot:recursive-continue-on-failure
    Validate library    ${legacy} and ${xml}
    Validate keyword 'Simple'
    Validate keyword 'Arguments'
    Validate keyword 'Types'
    Validate keyword 'Special Types'
    Validate keyword 'Union'
    Validate typedocs    ${legacy}

Validate library
    [Arguments]    ${buggy source}=False
    Name Should Be                     BackwardsCompatibility
    Version Should Be                  1.0
    Doc Should Start With              Library for testing backwards compatibility.\n
    Type Should Be                     LIBRARY
    Scope Should Be                    GLOBAL
    Generated Should Be Defined
    Spec Version Should Be Correct
    Should Have No Init
    Keyword Count Should Be            5
    Lineno Should Be                   1
    IF    ${buggy source}
         ${dir}    ${file} =           Split Path    ${BASE}.py
         Source Should Be              ${file}
    ELSE
         Source Should Be              ${BASE}.py
    END

Validate keyword 'Simple'
    Keyword Name Should Be             1    Simple
    Keyword Doc Should Be              1    Some doc.
    Keyword Tags Should Be             1    example
    Keyword Lineno Should Be           1    27
    Keyword Arguments Should Be        1

Validate keyword 'Arguments'
    Keyword Name Should Be             0    Arguments
    Keyword Doc Should Be              0    ${EMPTY}
    Keyword Tags Should Be             0
    Keyword Lineno Should Be           0    35
    Keyword Arguments Should Be        0    a    b=2    *c    d=4    e    **f

Validate keyword 'Types'
    Keyword Name Should Be             3    Types
    Keyword Doc Should Be              3    ${EMPTY}
    Keyword Tags Should Be             3
    Keyword Lineno Should Be           3    39
    Keyword Arguments Should Be        3    a: int    b: bool = True

Validate keyword 'Special Types'
    Keyword Name Should Be             2    Special Types
    Keyword Doc Should Be              2    ${EMPTY}
    Keyword Tags Should Be             2
    Keyword Lineno Should Be           2    43
    Keyword Arguments Should Be        2    a: Color    b: Size

Validate keyword 'Union'
    Keyword Name Should Be             4    Union
    Keyword Doc Should Be              4    ${EMPTY}
    Keyword Tags Should Be             4
    Keyword Lineno Should Be           4    47
    Keyword Arguments Should Be        4    a: int | bool

Validate typedocs
    [Arguments]    ${legacy}=False
    DataType Enum Should Be            0    Color    RGB colors.
    ...                                {"name": "RED", "value": "R"}
    ...                                {"name": "GREEN", "value": "G"}
    ...                                {"name": "BLUE", "value": "B"}
    DataType TypedDict Should Be       0    Size     Some size.
    ...                                {"key": "width", "type": "int", "required": "true"}
    ...                                {"key": "height", "type": "int", "required": "true"}
    IF    ${legacy}
        Usages Should Be               0    Enum         Color
        Usages Should Be               1    TypedDict    Size
    ELSE
        DataType Standard Should Be    0    boolean      Strings ``TRUE``,
        Usages Should Be               0    Standard     boolean    Types    Union
        Usages Should Be               1    Enum         Color      Special Types
        Usages Should Be               3    TypedDict    Size       Special Types
    END
