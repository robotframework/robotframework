*** Settings ***
Test Setup        No-break space       : :
Test Teardown     Ogham space mark     : :
Library  　  　  　OperatingSystem  　  　WITH NAME  　OS

*** Variables ***
${NO-BREAK SPACE} =         : :
${OGHAM SPACE MARK} =       : :  　  　# Trailing  　  　  　
${IDEOGRAPHIC　SPACE}　=    :　:  　  　  　  　  　  　

*** Test Cases ***
In test and keywords
    [Documentation]    Used in keyword name, arguments and assign.
    [ Tags ]    NBSP and Ogham
    ${x} =    No-break space        : :
    ${x} =    Ogham space mark       : :  　  　# Trailing  　  　  　
    ${x}　=    Ideographic　space    :　:  　  　  　  　  　  　

As separator
    No-break space    : :
     Ogham space mark    : :
　　　　Ideographic　space　　　　:　:

With pipes
| | No-break space  | : : |
| | Ogham space mark | : : |
|　|　Ideographic　space　|　:　:　|

*** Keywords ***
No-break space
    [ Arguments ]    ${arg}
    Log    ${arg}    formatter=repr
    Log    ${arg}
    Should be equal    ${arg}    : :
    Should be equal    ${arg}    ${NO-BREAK SPACE}
    Should be equal    ${arg}    ${NO-BREAK SPACE}

Ogham space mark
    [ Arguments ]    ${arg}
    Log    ${arg}    formatter=repr
    Log    ${arg}
    Should be equal    ${arg}    : :
    Should be equal    ${arg}    ${OGHAM SPACE MARK}
    Should be equal    ${arg}    ${OGHAM SPACE MARK}

Ideographic　space
    [　Arguments　]    ${arg}
    Log    ${arg}    formatter=repr
    Log    ${arg}
    Should　be　equal    ${arg}    :　:
    Should　be　equal    ${arg}    ${IDEOGRAPHIC SPACE}
    Should　be　equal    ${arg}    ${IDEOGRAPHIC　SPACE}

*** Test Cases　***
In header
    No operation

In test case　name
    No operation

In WITH NAME
    OS.Directory Should Exist    ${CURDIR}

In FOR separator
    FOR    ${index}    IN RANGE    1
        Should Be Equal    ${index}    ${0}
    END
    FOR    ${index}    ${item}    IN ENUMERATE    value
        Should Be Equal    ${index}: ${item}    0: value
    END
    FOR    ${tag}    IN　ZIP    ${TEST TAGS}
        Fail    Should not be executed
    END

In ELSE IF
    IF    False
        Fail    Should not be executed
    ELSE IF    False
        Fail    Should not be executed
    ELSE IF    False
        Fail    Should not be executed
    ELSE　IF    True
        Log    Should be executed
    END

In inline ELSE IF
    ${x} =    IF    False    Not run    ELSE IF    True    Set Variable    NBSP
    ${y} =    IF    False    Not run    ELSE IF    True    Set Variable    OGHAM
    ${z} =    IF    False    Not run    ELSE　IF    True    Set Variable    IDEOGRAPHIC
    Should Be Equal    ${x}:${y}:${z}    NBSP:OGHAM:IDEOGRAPHIC
