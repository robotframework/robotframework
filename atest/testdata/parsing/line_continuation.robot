...    Ignored usage

*** Settings ***
...    Part of header above
Documentation
...    First row.
...    Second row.
...
...    Second paragraph
...    !
\    ...    Does not work anymore in RF 3.2.
...    !
Metadata         Name
...              1.1
...              1.2
...
...              2.1
...              2.2
...              2.3
...
...              3.1
# Some comments here to complicate parsing even more ...
Default Tags    ...    t1    t2    t3    t4
...             t4     t5    \     t6
...             # more comments
...             \      t7    t8
...             t9
Library
...    OperatingSystem
Test Teardown    Log Many
...    1st
...
...    2nd last
...

*** Variables ***
...    # Part of header above
${STRING}    first
...
...          third
...          # Not ignoring empty
# Comments, comments, comments, ...
\    ...    Does not work anymore in RF 3.2.
@{list}    ...    hello
...    world
...
   ...    ...
      ...    !!!

*** Test Cases ***
Multiline import
    Directory Should Exist    .

Multiline variables
    Should Be Equal    ${STRING}    first${SPACE * 2}third${SPACE}
    Should Be True    $LIST    ['...', 'hello', 'world', '...', '!!!']

Multiline arguments with library keyword
    Log Many    one    two
    ...    three
    ...
...    four    five

Multiline arguments with user keyword
    UK Log Many
    ...    ${1}
       ...
...    ${2}    ${3}
             ...    ${4}
                ...    ${5}

Multiline assignment
    ${a}    ${b}    ${c}    ${d} =
    ...    Create List    1    2     3    4
    Should Be Equal    ${a}-${b}-${c}-${d}    1-2-3-4
    ${a}
    ...    ${b}
    ...    ${c}    ${d} =    Create List
    ...    1    2     3    4
    Should Be Equal    ${a}-${b}-${c}-${d}    1-2-3-4

Multiline in user keyword
    Multiline in user keyword

Multiline test settings
    [Documentation]    One.
    ...    Two.
...    Three.
    ...
                                ...    Second paragraph.
    [Tags]
    ...    my1    my2    my3
    ...    my4
    ...
    ...    my5
    [Setup]    Log Many
    ...    first
    ...
    ...    last
    No Operation

Multiline user keyword settings and control structures
    ${x} =    Multiline User Keyword Settings And Control Structures    1    2
    Should Be True    ${x} == [str(i) if i != 8 else '' for i in range(1, 10)]
    ${x} =    Multiline User Keyword Settings And Control Structures
    ...    1    2    3    4    5    r1    r2    r3
    Should Be True    ${x}[:5] == [str(i) for i in range(1, 6)]
    Should Be True    ${x}[5:] == ['r1', 'r2', 'r3', '6', '7', '', '9']

Multiline FOR Loop declaration
    ${result} =    Set Variable    ${EMPTY}
    FOR    ${item}    IN    a    b
    ...                     c
        ${result} =    Set Variable    ${result}${item}
    END
    Should Be Equal    ${result}    abc
    FOR
    ...    ${item}
    ...    IN
    ...    c
    ...    b
        ${result} =    Set Variable    ${result.replace('${item}', '')}
    END
    Should Be Equal    ${result}    a
    FOR
    ...    ${item}
       ...    IN RANGE
          ...    1
             ...    2
        ${result} =    Set Variable    ${result}${item}
    END
    Should Be Equal    ${result}    a1
    FOR    ${i1}    ${i2}    IN
    ...    b    2
    ...    c    3
        ${result} =    Set Variable    ${result}${i1}${i2}
    END
    Should Be Equal    ${result}    a1b2c3
    FOR    ${item}    IN
        ...    a    b    c
        ${result} =    Set Variable    ${result.replace('${item}', '')}
    END
    Should Be Equal    ${result}    123
    FOR    ${item}    IN RANGE    1
       ...    4
       ${result} =    Set Variable    ${result.replace('${item}', '')}
    END
    Should Be Equal    ${result}    ${EMPTY}

Multiline in FOR loop body
    ${result} =    Set Variable    ${EMPTY}
    FOR    ${item}    IN    a    b    c
        ${item} =    Set Variable
        ...    ${item.upper()}
        ${result} =    Set Variable
    ...    ${result}${item}
        ${x} =
        ...    Catenate
           ...     1    2    3
              ...    a
                 ...     b
                    ...        ${item.lower()}
    END
    Should Be Equal    ${result}    ABC
    Should Be Equal    ${x}    1 2 3 a b c

Invalid usage in test
    ...
    [Documentation]    FAIL Keyword name cannot be empty.
    No operation

Invalid usage in user keyword
    [Documentation]    FAIL Keyword name cannot be empty.
    Invalid Usage In UK

Invalid usage in keyword call
    [Documentation]    FAIL
    ...   No keyword with name '\\' found. If it is used inside a for loop, remove escaping backslashes and end the loop with 'END'.
    Log Many   1
    ...   2
    \    ...   Does not work anymore in 3.2

*** Keywords ***
UK log many
    [Arguments]    @{msgs}
    Log Many    @{msgs}

Multiline in user keyword
    Log Many
    ...    1
    ...    2
    UK Log Many
    ...    xxx
    ${y} =    Create List    1    2
    ...    3    4    5
    Should Be True    ${y} == [str(i) for i in range(1,6)]
    ${a}
    ...    ${b} =
    ...    Create List
    ...    aaa
    ...    bbb
    Should Be Equal    ${a}-${b}    aaa-bbb

Multiline user keyword settings and control structures
    [Arguments]    ${a1}    ${a2}    ${a3}=3
    ...    ${a4}=4
    ...    ${a5}=5    @{rest}
    [Tags]
    ...    keyword
    ...
    ...    tags
    Should Be Equal    ${a1}    1
    Should Be Equal    ${a2}    2
    Should Be Equal    ${a3}    3
    Should Be Equal    ${a4}    4
    Should Be Equal    ${a5}    5
    RETURN    ${a1}    ${a2}
    ...    ${a3}    ${a4}    ${a5}
       ...    @{rest}
          ...    6
             ...    7
                ...
                   ...    9
   [Teardown]    Log
   ...    Bye!
   ...    level=INFO

Invalid usage in UK
    ...
    No operation
