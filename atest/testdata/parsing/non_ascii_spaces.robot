*** Settings ***
Test Setup        No-break space       : :
Test Teardown     Ogham space mark     : :

*** Variables ***
${NO-BREAK SPACE} =         : :
${OGHAM SPACE MARK} =       : :
${IDEOGRAPHIC　SPACE}　=    :　:

*** Test Cases ***
In test and keywords
    [Documentation]    Used in keyword name, arguments and assign.
    ...                In RF 3.2 arguments shouldn't be normalized.
    [ Tags ]    NBSP and Ogham
    ${x} =    No-break space        : :
    ${x} =    Ogham space mark       : :
    ${x}　=    Ideographic　space    :　:

As separator
    [Documentation]    In RF 3.1 only NBSP works
    No-break space    : :

With pipes
    [Documentation]    In RF 3.1 only NBSP works
| | No-break space  | : : |

*** Keywords ***
No-break space
    [ Arguments ]    ${arg}
    Log    ${arg}    repr=True
    Should be equal    ${arg}    : :
    Should be equal    ${arg}    ${NO-BREAK SPACE}
    Should be equal    ${arg}    ${NO-BREAK SPACE}

Ogham space mark
    [ Arguments ]    ${arg}
    Log    ${arg}    repr=True
    Should be equal    ${arg}    : :
    Should be equal    ${arg}    ${OGHAM SPACE MARK}
    Should be equal    ${arg}    ${OGHAM SPACE MARK}

Ideographic　space
    [　Arguments　]    ${arg}
    Log    ${arg}    repr=True
    Should　be　equal    ${arg}    : :
    Should　be　equal    ${arg}    ${IDEOGRAPHIC SPACE}
    Should　be　equal    ${arg}    ${IDEOGRAPHIC　SPACE}

*** Test Cases　***
In header
    No operation
