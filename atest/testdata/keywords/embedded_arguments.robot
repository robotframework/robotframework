*** Settings ***
Resource        resources/embedded_args_in_uk_1.robot
Resource        resources/embedded_args_in_uk_2.robot

*** Test Cases ***
Embedded Arguments In User Keyword Name
    ${name}  ${book} =  User Peke Selects Advanced Python From Webshop
    Should Be Equal  ${name}-${book}  Peke-Advanced Python
    ${name}  ${book} =  User Juha Selects Playboy From Webshop
    Should Be Equal  ${name}-${book}  Juha-Playboy

Embedded And Positional Arguments Do Not Work Together
    [Documentation]  FAIL Keyword 'User \${user} Selects \${item} From Webshop' expected 0 arguments, got 1.
    Given this "usage" with @{EMPTY} works  @{EMPTY}
    Then User Invalid Selects Invalid From Webshop  invalid

Complex Embedded Arguments
    Given this "feature" works
    When this "test case" is *executed*
    Then this "issue" is about to be done!

Argument Namespaces with Embedded Arguments
    ${var}=  Set Variable  hello
    My embedded warrior
    Should be equal  ${var}  hello

Embedded Arguments as Variables
    ${name}  ${item} =  User ${42} Selects ${EMPTY} From Webshop
    Should Be Equal  ${name}-${item}  42-
    ${name}  ${item} =  User ${name} Selects ${SPACE * 10} From Webshop
    Should Be Equal  ${name}-${item}  42-${SPACE*10}
    ${name}  ${item} =  User ${name} Selects ${TEST TAGS} From Webshop
    Should Be Equal  ${name}  ${42}
    Should Be True  ${item} == []

Non-Existing Variable in Embedded Arguments
    [Documentation]  FAIL Non-existing variable '${non existing}'.
    User ${non existing} Selects ${variables} From Webshop

Non-Existing Variable in Embedded Arguments and Positional Arguments
    [Documentation]  FAIL Keyword 'User \${user} Selects \${item} From Webshop' expected 0 arguments, got 2.
    User ${non existing} Selects ${variables} From Webshop    invalid    args

Non-Existing Variable in Embedded Arguments and in Positional Arguments
    [Documentation]  FAIL Non-existing variable '\${nonex pos}'.
    User ${nonex emb} Selects ${variables} From Webshop    ${nonex pos}

Custom Embedded Argument Regexp
    [Documentation]  FAIL No keyword with name 'Result of a + b is fail' found.
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

Grouping Custom Regexp
    ${matches} =  Grouping Custom Regexp(erts)
    Should Be Equal  ${matches}  Custom-Regexp(erts)
    ${matches} =  Grouping Cuts Regexperts
    Should Be Equal  ${matches}  Cuts-Regexperts

Custom Regexp Matching Variables
    [Documentation]  FAIL  42 != foo
    ${foo}  ${bar}  ${zap} =  Create List  foo  bar  zap
    I execute "${foo}"
    I execute "${bar}" with "${zap}"
    I execute "${42}"

Custom Regexp Matching Variables When Regexp Does No Match Them
    Result of ${3} + ${-1} is ${2}
    Result of ${40} - ${-2} is ${42}
    ${s42} =  Set Variable  42
    I want ${42} and ${s42} as variables

Escaping Values Given As Embedded Arguments
    ${name}  ${item} =  User \${nonex} Selects \\ From Webshop
    Should Be Equal  ${name}-${item}  \${nonex}-\\
    ${name}  ${item} =  User \ Selects \ \ From Webshop
    Should Be Equal  ${name}-${item}  ${EMPTY}-${SPACE}

Embedded Arguments Syntax Is Case Insensitive
    x Gets y From The z
    x gets y from the z
    x GETS y from the z
    x gets y FROM THE z

Embedded Arguments Syntax is Space Sensitive
    [Documentation]  FAIL No keyword with name 'User Janne Selects x fromwebshop' found.
    User Janne Selects x from webshop
    User Janne Selects x fromwebshop

Embedded Arguments Syntax is Underscore Sensitive
    [Documentation]  FAIL No keyword with name 'User Janne Selects x from_webshop' found.
    User Janne Selects x from webshop
    User Janne Selects x from_webshop

Embedded Arguments In Resource File
    ${ret} =  Juha Uses Resource File
    Should Be Equal  ${ret}  Juha-Resource

Embedded Arguments In Resource File Used Explicitly
    ${ret} =  embedded_args_in_uk_1.peke uses resource file
    Should Be Equal  ${ret}  peke-resource
    embedded_args_in_uk_2.-r1-r2-+r1+

Keyword with normal arguments cannot have embedded arguments
    [Documentation]  FAIL No keyword with name 'Keyword with value and normal args' found. Did you mean:
    ...    ${SPACE * 4}Keyword With ${variable} And Normal Args
    Keyword with ${variable} and normal args  foo  bar
    Keyword with value and normal args  foo  bar

Keyword with embedded args can be used as "normal" keyword
    [Documentation]  FAIL Replacing variables from keyword return value failed: Non-existing variable '${user}'.
    Normal keyword with ${variable} in name
    User ${user} Selects ${item} From Webshop

Keyword Matching Multiple Keywords In Test Case File
    [Documentation]  FAIL Test case file contains multiple keywords matching name 'foo+tc+bar-tc-zap'\n Found: '${a}-tc-${b}' and '${a}+tc+${b}'
    foo+tc+bar
    foo-tc-bar
    foo+tc+bar+tc+zap
    foo+tc+bar-tc-zap

Keyword Matching Multiple Keywords In One Resource File
    [Documentation]  FAIL Resource file 'embedded_args_in_uk_1' contains multiple keywords matching name 'foo+r1+bar-r1-zap'\n Found: '${a}-r1-${b}' and '${a}+r1+${b}'
    foo+r1+bar
    foo-r1-bar
    foo+r1+bar-r1-zap

Keyword Matching Multiple Keywords In Different Resource Files
    [Documentation]  FAIL Multiple keywords with name 'foo-r1-bar-r2-zap' found.\n Give the full name of the keyword you want to use.\n Found: 'embedded_args_in_uk_1.foo-r1-bar-r2-zap' and 'embedded_args_in_uk_2.foo-r1-bar-r2-zap'
    foo-r1-bar
    foo-r2-bar
    foo-r1-bar-r2-zap

Keyword Matching Multiple Keywords In One And Different Resource Files
    [Documentation]  FAIL Resource file 'embedded_args_in_uk_1' contains multiple keywords matching name '-r1-r2-+r1+'\n Found: '${a}-r1-${b}' and '${a}+r1+${b}'
    -r1-r2-+r1+

*** Keywords ***
User ${user} Selects ${item} From Webshop
    Log  This is always executed
    [Return]  ${user}  ${item}

${prefix:Given|When|Then} this "${item}" ${no good name for this arg ...}
    Log  ${item}-${no good name for this arg ...}

My embedded ${var}
    Should be equal  ${var}  warrior

${x:x} gets ${y:\w} from the ${z:.}
    Should Be Equal  ${x}-${y}-${z}  x-y-z

Keyword with ${variable} and normal args
    [Arguments]  ${arg1}  ${arg2}
    Variable Should Not Exist  ${variable}
    Should Be Equal  ${arg1}  foo
    Should Be Equal  ${arg2}  bar

Normal keyword with ${variable} in name
    Variable Should Not Exist  ${variable}

${a}-tc-${b}
    Log  ${a}-tc-${b}

${a}+tc+${b}
    Log  ${a}+tc+${b}

I execute "${x:[^"]*}"
    Should Be Equal  ${x}  foo

I execute "${x:bar}" with "${y:...}"
    Should Be Equal  ${x}  bar
    Should Be Equal  ${y}  zap

Result of ${a:\d+} ${operator:[+-]} ${b:\d+} is ${result}
    Should Be True  ${a} ${operator} ${b} == ${result}

I want ${integer:whatever} and ${string:everwhat} as variables
    Should Be Equal  ${integer}  ${42}
    Should Be Equal  ${string}   42

Today is ${date:\d{4\}-\d{2\}-\d{2\}}
    Should Be Equal  ${date}  2011-06-21

Today is ${day1:\w{6,9\}} and tomorrow is ${day2:\w{6,9\}}
    Should Be Equal  ${day1}  Tuesday
    Should Be Equal  ${day2}  Wednesday

Literal ${Curly:{} Brace
    Should Be Equal  ${Curly}  {

Literal ${Curly:\}} Brace
    Should Be Equal  ${Curly}  }

Custom Regexp With Escape Chars e.g. ${1E:\\\\}, ${2E:\\\\\\\\} and ${PATH:c:\\\\temp\\.*}
    Should Be Equal  ${1E}    \\
    Should Be Equal  ${2E}    \\\\
    Should Be Equal  ${PATH}  c:\\temp\\test.txt

Custom Regexp With ${pattern:\\\\\}}
    Should Be Equal  ${pattern}    \\}

Grouping ${x:Cu(st|ts)(om)?} ${y:Regexp\(?erts\)?}
    [Return]  ${x}-${y}

Regexp extensions like ${x:(?x)re} are not supported
    This is not executed

Invalid ${x:(} Regexp
    This is not executed
