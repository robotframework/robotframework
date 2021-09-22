*** Settings ***
Variables         extended_variables.py

*** Variables ***
${X}              X
${Y}              Y
@{LIST}           ${42}    foo    ${None}

*** Test Cases ***
Using Attribute
    Should Be Equal    ${OBJ.name}    dude
    Should Be Equal    ${ o_B J __ .name}    dude

Calling Method
    Should Be Equal    ${OBJ.greet()}    dude says hi!
    Should Be Equal    ${OBJ.greet('dudette')}    dude says hi to dudette!
    Should Be Equal    ${OBJ.name.capitalize()}    Dude
    Should Be Equal    ${SPACE.__len__()}    ${1}

Accessing List
    Should Be Equal    ${LIST[0]} ${LIST[1]}    42 foo
    Should Be Equal    ${LIST[2]}    ${None}
    Should Be Equal    ${LIST[-1]} ${LIST[-2]}    None foo

Accessing Dictionary
    ${dict} =    Evaluate    {'a': 1, 42: 'b'}
    Should Be Equal    ${dict['a']}    ${1}
    Should Be Equal    ${dict[42]}    b

Multiply
    [Documentation]    FAIL STARTS: Resolving variable '\${3.0 * 2}' failed: SyntaxError:
    Should Be Equal    ${SPACE * 3}    ${SPACE}${SPACE}${SPACE}
    Should Be Equal    ${3 * 42}    ${126}
    Should Be Equal    ${3 * 2.0}    ${6}
    Log Many    Having float first fails    ${3.0 * 2}

Failing When Base Name Does Not Exist
    [Documentation]    FAIL Resolving variable '\${nonexisting.whatever}' failed: Variable '\${nonexisting}' not found.
    Log    ${nonexisting.whatever}

Failing When Base Name Starts With Existing Variable 1
    [Documentation]    FAIL Variable '\${nonexisting}' not found.
    Log    ${None}
    Log    ${nonexisting}

Failing When Base Name Starts With Existing Variable 2
    [Documentation]    FAIL STARTS: Variable '\${lista}' not found.
    Log    ${list}
    Log    ${lista}

Testing Extended Var Regexp
    [Documentation]    FAIL STARTS: Resolving variable '\${var..upper()}' failed: SyntaxError:
    Length Should Be    ${/*3}    ${1 * 3}
    Should Be Equal    ${/.upper()}    ${/ * 1}
    ${var}    ${var.}    ${var.upper} =    Set Variable    value    Value    VALUE
    Should Be Equal    ${v a r .}    Value
    Should Be Equal    ${__ VAR . UPPER __}    VALUE
    Should Be Equal    ${var.}    ${var.capitalize()}
    Should Be Equal    ${var.upper}    ${_ V _ A _ R _ . upper ( ) }
    Log Many    So this works ${var.upper()}    but this does not ${var..upper()}

Base name contains non-ASCII characters
    ${äiti}=    Set Variable    hyvä
    Should Be Equal    ${äiti.upper()}    HYVÄ
    ${isä}=    Set Variable    hyvä
    Should Be Equal    ${isä.upper()}    HYVÄ

Escape characters and curly braces
    [Documentation]    Escape characters in the variable body are left alone
    ...                and thus can be used in evaluated expression without
    ...                additional escaping. Exceptions to this rule are escapes
    ...                before curly braces as well as before literal strings
    ...                looking like variables. These escapes are needed to
    ...                make the whole variable valid and are removed. Matching
    ...                curly braces don't need to be escaped.
    [Template]    Should Be Equal
    ${X + '\n'}               X\n
    ${X + u'\xe4'}            Xä
    ${X + '\${Y}'}            X\${Y}
    ${X + '\\${Y}'}           X\\Y
    ${X + '$\{Y\}'}           X\${Y}
    ${X + '\$\{Y\}'}          X\\\${Y}
    ${X + '\\'}               X\\
    ${X + '\}'}               X}
    ${X + '\{'}               X{
    ${X + '{}'}               X{}
    ${X + {'k': 'v'}['k']}    Xv
    ${X + __import__('re').match('(\d{2})${Y}\\s{2}', '1${2}Y\t\r').group(${1})}
    ...                       X12

Failing When Attribute Does Not exists 1
    [Documentation]    FAIL STARTS: Resolving variable '\${OBJ.nonex}' failed: AttributeError:
    Log    ${OBJ.nonex}

Failing When Attribute Does Not exists 2
    [Documentation]    FAIL STARTS: Resolving variable '\${OBJ.nonex_method()}' failed: AttributeError:
    Log    ${OBJ.nonex_method()}

Failing When Calling Method With Wrong Number Of Arguments
    [Documentation]    FAIL STARTS: Resolving variable '\${OBJ.greet('too', 'many')}' failed: TypeError:
    Log    ${OBJ.greet('too', 'many')}

Failing When Method Raises Exception
    [Documentation]    FAIL Resolving variable '\${OBJ.greet('FAIL')}' failed: ValueError
    Log    ${OBJ.greet('FAIL')}

Fail When Accessing Item Not In List
    [Documentation]    FAIL STARTS: Resolving variable '\${LIST[30]}' failed: IndexError:
    Log    ${LIST[30]}

Fail When Accessing Item Not In Dictionary
    [Documentation]    FAIL STARTS: Resolving variable '\${dict['xxx']}' failed: KeyError:
    ${dict} =    Evaluate    {}
    Log    ${dict['xxx']}

Failing For Syntax Error
    [Documentation]    FAIL STARTS: Resolving variable '\${OBJ.greet('no end quote)}' failed: SyntaxError:
    Log    ${OBJ.greet('no end quote)}
