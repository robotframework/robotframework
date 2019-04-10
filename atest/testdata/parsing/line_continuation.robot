...    Ignored usage

*** Settings ***
...    Invalid usage
Documentation
...    First row.
...    Second row.
...
...    Second paragraph
...    !
\    ...    !    # Leading '\' deprecated in RF 3.1.2.
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
...    # Invalid usage
${STRING}    first
...
...          third
...          # Ignoring empty
# Comments, comments, comments, ...
@{list}    ...    hello
...    world
...
   ...    ...
      ...    !!!

*** Test Cases ***
Multiline import
    Directory Should Exist    .

Multiline variables
    Should Be Equal    ${STRING}    first third
    Should Be True    $LIST    ['...', 'hello', 'world', '...', '!!!']

Multiline arguments with library keyword
    Log Many    one    two
    ...    three
    ...
    \    ...    four    five    # Leading '\' deprecated in RF 3.1.2.

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
    \   ...    Three.         # Leading '\' deprecated in RF 3.1.2.
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

Multiline user keyword settings
    ${x} =    Multiline User Keyword Settings    1    2
    Should Be True    ${x} == [str(i) for i in range(1,10) if i != 8]
    ${x} =    Multiline User Keyword Settings
    ...    1    2    3    4    5    r1    r2    r3
    Should Be True    ${x[:5]} == [str(i) for i in range(1,6)]
    Should Be True    ${x[5:8]} == ['r1','r2','r3']
    Should Be True    ${x[9:]} == ['7', '9']

Multiline for Loop declaration
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

Multiline in for loop body
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

Invalid usage in test and user keyword
    ...
    [Documentation]    FAIL This is executed after all!
    Invalid Usage In UK

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

Multiline user keyword settings
    [Arguments]    ${a1}    ${a2}    ${a3}=3
    ...    ${a4}=4
    ...    ${a5}=5    @{rest}
    Should Be Equal    ${a1}    1
    Should Be Equal    ${a2}    2
    Should Be Equal    ${a3}    3
    Should Be Equal    ${a4}    4
    Should Be Equal    ${a5}    5
    [Return]    ${a1}    ${a2}
    ...    ${a3}    ${a4}    ${a5}
       ...    @{rest}
          ...    6
             ...    7
                ...
                   ...    9

Invalid usage in UK
    ...
    Fail    This is executed after all!
