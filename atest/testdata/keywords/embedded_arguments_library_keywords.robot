*** Settings ***
Library        resources/embedded_args_in_lk_1.py
Library        resources/embedded_args_in_lk_2.py

*** Variables ***
${INDENT}         ${SPACE * 4}
${foo}            foo
${bar}            bar
${zap}            zap
@{list}           first    ${2}    third

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
    Should Be Equal    ${item}    ${{[]}}

Embedded Arguments as List And Dict Variables
    ${inp1}    ${inp2} =    Evaluate    (1, 2, 3, 'neljä'), {'a': 1, 'b': 2}
    ${out1}    ${out2} =    User @{inp1} Selects &{inp2} From Webshop
    Should Be Equal    ${out1}      ${{list($inp1)}}
    Should Be Equal    ${out2}      ${inp2}
    Should Be Equal    ${out2.a}    ${1}
    Should Be Equal    ${out2.b}    ${2}

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
    Literal {} Braces

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
    [Documentation]    FAIL bar != foo
    I execute "${foo}"
    I execute "${bar}" with "${zap}"
    I execute "${bar}"

Non Matching Variable Is Accepted With Custom Regexp (But Not For Long)
    [Documentation]    FAIL    foo != bar    # ValueError: Embedded argument 'x' got value 'foo' that does not match custom pattern 'bar'.
    I execute "${foo}" with "${bar}"

Partially Matching Variable Is Accepted With Custom Regexp (But Not For Long)
    [Documentation]    FAIL     ba != bar    # ValueError: Embedded argument 'x' got value 'ba' that does not match custom pattern 'bar'.
    I execute "${bar[:2]}" with "${zap * 2}"

Non String Variable Is Accepted With Custom Regexp
    [Documentation]    FAIL 42 != foo
    Result of ${3} + ${-1} is ${2}
    Result of ${40} - ${-2} is ${42}
    I execute "${42}"

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
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'foo+lib+bar-lib-zap' found:
    ...    ${INDENT}embedded_args_in_lk_1.\${a}+lib+\${b}
    ...    ${INDENT}embedded_args_in_lk_1.\${a}-lib-\${b}
    foo+lib+bar
    foo-lib-bar
    foo+lib+bar+lib+zap
    foo+lib+bar-lib-zap

Keyword Matching Multiple Keywords In Different Library Files
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'foo*lib*bar' found:
    ...    ${INDENT}embedded_args_in_lk_1.\${a}*lib*\${b}
    ...    ${INDENT}embedded_args_in_lk_2.\${a}*lib*\${b}
    foo*lib*bar

Keyword with only embedded arguments doesn't accept normal arguments
    [Documentation]    FAIL Keyword 'embedded_args_in_lk_1.User \${user} Selects \${item} From Webshop' expected 0 arguments, got 1.
    Given this "usage" with @{EMPTY} works    @{EMPTY}
    Then User Invalid Selects Invalid From Webshop    invalid

Keyword with embedded args cannot be used as "normal" keyword
    [Documentation]    FAIL Variable '\${user}' not found.
    User ${user} Selects ${item} From Webshop

Keyword with both embedded and normal arguments
    Number of horses should be    2
    Number of horses should be    2    swimming
    Number of dogs should be    count=3

Conversion with embedded and normal arguments
    [Documentation]    FAIL ValueError: Argument 'num1' got value 'bad' that cannot be converted to integer.
    Conversion with embedded 42 and normal    42
    Conversion with embedded bad and normal    bad

Keyword with both embedded and normal arguments with too few arguments
    [Documentation]    FAIL Keyword 'embedded_args_in_lk_1.Number of \${animals} should be' expected 1 to 2 arguments, got 0.
    Number of horses should be

Must accept at least as many positional arguments as there are embedded arguments
    [Documentation]    FAIL No keyword with name 'Wrong number of embedded args' found.
    Wrong number of embedded args

Optional Non-Embedded Args Are Okay
    @{ret} =    Optional Non-Embedded Args Are Okay
    Should Be Equal    ${ret}    ${{['Embedded', 'Okay', 3]}}
    @{ret} =    Optional Non-Embedded Args Are Usable    Since RF 7!
    Should Be Equal    ${ret}    ${{['Embedded', 'Usable', 'Since RF 7!']}}

Varargs With Embedded Args Are Okay
    @{ret} =    Varargs With Embedded Args are Okay
    Should Be Equal    ${ret}    ${{['Embedded', 'Okay']}}
    @{ret} =    Varargs With R Args are F    ${SPACE}    7    .    0    !    !    !
    Should Be Equal    ${{''.join($ret)}}    RF 7.0!!!

Lists are not expanded when keyword accepts varargs
    @{ret} =    Varargs With ${list} Args are Okay
    Should Be Equal    ${ret}    ${{[['first', 2, 'third'], 'Okay']}}
    @{ret} =    Varargs With @{list} Args are Okay
    Should Be Equal    ${ret}    ${{[['first', 2, 'third'], 'Okay']}}

Same name with different regexp works
    It is a car
    It is a dog
    It is a cow

Same name with different regexp matching multiple fails
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'It is a cat' found:
    ...    ${INDENT}embedded_args_in_lk_1.It is \${animal:a (cat|cow)}
    ...    ${INDENT}embedded_args_in_lk_1.It is \${animal:a (dog|cat)}
    It is a cat

Same name with same regexp fails
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'It is totally same' found:
    ...    ${INDENT}embedded_args_in_lk_1.It is totally ${same}
    ...    ${INDENT}embedded_args_in_lk_1.It is totally ${same}
    It is totally same
