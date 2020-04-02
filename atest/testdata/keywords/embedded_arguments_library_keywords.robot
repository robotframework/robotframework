*** Settings ***
Library        resources/embedded_args_in_lk_1.py
Library        resources/embedded_args_in_lk_2.py

*** Variables ***
${INDENT}         ${SPACE * 4}

*** Test Cases ***
Embedded Arguments In Library Keyword Name
    ${name}  ${book} =  User Peke Selects Advanced Python From Webshop
    Should Be Equal  ${name}-${book}  Peke-Advanced Python
    ${name}  ${book} =  User Juha selects Playboy from webshop
    Should Be Equal  ${name}-${book}  Juha-Playboy

Complex Embedded Arguments
    # Notice that Given/When/Then is part of the keyword name
    Given this "feature" works
    When this "test case" is *executed*
    Then this "issue" is about to be done!

Embedded Arguments with BDD Prefixes
    Given user x selects y from webshop
    When user x selects y from webshop
    ${x}    ${y} =    Then user x selects y from webshop
    Should Be Equal    ${x}-${y}    x-y

Argument Namespaces with Embedded Arguments
    ${var}=    Set Variable    hello
    My embedded warrior
    Should be equal    ${var}    hello

Embedded Arguments as Variables
    ${name}    ${item} =    User ${42} Selects ${EMPTY} From Webshop
    Should Be Equal    ${name}-${item}    42-
    ${name}    ${item} =    User ${name} Selects ${SPACE * 10} From Webshop
    Should Be Equal    ${name}-${item}    42-${SPACE*10}
    ${name}    ${item} =    User ${name} Selects ${TEST TAGS} From Webshop
    Should Be Equal    ${name}    ${42}
    Should Be True    ${item} == []

Non-Existing Variable in Embedded Arguments
    [Documentation]    FAIL Variable '${non existing}' not found.
    User ${non existing} Selects ${variables} From Webshop

Custom Embedded Argument Regexp
    [Documentation]    FAIL No keyword with name 'Result of a + b is fail' found.
    I execute "foo"
    I execute "bar" with "zap"
    Result of 1 + 1 is 2
    Result of 43 - 1 is 42
    Result of a + b is fail

Custom Regexp With Curly Braces
    Today is 2011-06-21
    Today is Tuesday and tomorrow is Wednesday
    Literal { Brace
    Literal } Brace

Custom Regexp With Escape Chars
    Custom Regexp With Escape Chars e.g. \\, \\\\ and c:\\temp\\test.txt
    Custom Regexp With \\}
    Custom Regexp With \\{
    Custom Regexp With \\{}

Grouping Custom Regexp
    ${matches} =    Grouping Custom Regexp(erts)
    Should Be Equal    ${matches}    Custom-Regexp(erts)
    ${matches} =    Grouping Cuts Regexperts
    Should Be Equal    ${matches}    Cuts-Regexperts

Custom Regexp Matching Variables
    [Documentation]    FAIL 42 != foo
    ${foo}    ${bar}    ${zap} =    Create List    foo    bar    zap
    I execute "${foo}"
    I execute "${bar}" with "${zap}"
    I execute "${42}"

Custom Regexp Matching Variables When Regexp Does No Match Them
    Result of ${3} + ${-1} is ${2}
    Result of ${40} - ${-2} is ${42}
    ${s42} =    Set Variable    42
    I want ${42} and ${s42} as variables

Escaping Values Given As Embedded Arguments
    ${name}    ${item} =    User \${nonex} Selects \\ From Webshop
    Should Be Equal    ${name}-${item}    \${nonex}-\\
    ${name}    ${item} =    User \ Selects \ \ From Webshop
    Should Be Equal    ${name}-${item}    ${EMPTY}-${SPACE}

Embedded Arguments Syntax is Space Sensitive
    [Documentation]    FAIL No keyword with name 'User Janne Selects x fromwebshop' found.
    User Janne Selects x from webshop
    User Janne Selects x fromwebshop

Embedded Arguments Syntax is Underscore Sensitive
    [Documentation]    FAIL No keyword with name 'User Janne Selects x from_webshop' found.
    User Janne Selects x from webshop
    User Janne Selects x from_webshop

Keyword Matching Multiple Keywords In Library File
    [Documentation]    FAIL Test library 'embedded_args_in_lk_1' contains multiple keywords matching name 'foo+lib+bar-lib-zap':
    ...    ${INDENT}\${a}+lib+\${b}
    ...    ${INDENT}\${a}-lib-\${b}
    foo+lib+bar
    foo-lib-bar
    foo+lib+bar+lib+zap
    foo+lib+bar-lib-zap

Keyword Matching Multiple Keywords In Different Library Files
    [Documentation]    FAIL Multiple keywords with name 'foo*lib*bar' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${INDENT}embedded_args_in_lk_1.foo*lib*bar
    ...    ${INDENT}embedded_args_in_lk_2.foo*lib*bar
    foo*lib*bar

Embedded And Positional Arguments Do Not Work Together
    [Documentation]    FAIL Positional arguments are not allowed when using embedded arguments.
    Given this "usage" with @{EMPTY} works    @{EMPTY}
    Then User Invalid Selects Invalid From Webshop    invalid

Keyword with embedded args cannot be used as "normal" keyword
    [Documentation]    FAIL Variable '\${user}' not found.
    User ${user} Selects ${item} From Webshop

Embedded argument count must match accepted arguments
    [Documentation]  FAIL No keyword with name 'Wrong number of embedded args' found.
    Wrong number of embedded args

Optional Non-Embedded Args Are Okay
    Optional Non-Embedded Args Are Okay

Star Args With Embedded Args Are Okay
    @{ret} =    Star Args With Embedded Args are Okay
    @{args} =    Create List    Embedded    Okay
    Should Be Equal    ${ret}    ${args}

Same name with different regexp works
    It is a car
    It is a dog
    It is a cow

Same name with different regexp matching multiple fails
    [Documentation]    FAIL
    ...    Test library 'embedded_args_in_lk_1' contains multiple keywords matching name 'It is a cat':
    ...    ${INDENT}It is ${animal:a (cat|cow)}
    ...    ${INDENT}It is ${animal:a (dog|cat)}
    It is a cat

Same name with same regexp fails
    [Documentation]    FAIL
    ...    Test library 'embedded_args_in_lk_1' contains multiple keywords matching name 'It is totally same':
    ...    ${INDENT}It is totally ${same}
    ...    ${INDENT}It is totally ${same}
    It is totally same
