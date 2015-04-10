*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/embedded_arguments.robot
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Test Cases ***
Embedded Arguments In User Keyword Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    This is always executed
    Should Be Equal    ${tc.kws[0].name}    \${name}, \${book} = User Peke Selects Advanced Python From Webshop
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    This is always executed
    Should Be Equal    ${tc.kws[2].name}    \${name}, \${book} = User Juha Selects Playboy From Webshop

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    feature-works
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    test case-is *executed*
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    issue-is about to be done!

Embedded Arguments with BDD Prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    Given user x selects y from webshop
    Should Be Equal    ${tc.kws[1].name}    When user x selects y from webshop
    Should Be Equal    ${tc.kws[2].name}    \${x}, \${y} = Then user x selects y from webshop

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${name}, \${item} = User \${42} Selects \${EMPTY} From Webshop
    Should Be Equal    ${tc.kws[2].name}    \${name}, \${item} = User \${name} Selects \${SPACE * 10} From Webshop

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    User \${non existing} Selects \${variables} From Webshop

Non-Existing Variable in Embedded Arguments and Positional Arguments
    Check Test Case    ${TEST NAME}

Non-Existing Variable in Embedded Arguments and in Positional Arguments
    Check Test Case    ${TEST NAME}

Custom Embedded Argument Regexp
    Check Test Case    ${TEST NAME}

Custom Regexp With Curly Braces
    Check Test Case    ${TEST NAME}

Custom Regexp With Escape Chars
    Check Test Case    ${TEST NAME}

Grouping Custom Regexp
    Check Test Case    ${TEST NAME}

Custom Regexp Matching Variables
    Check Test Case    ${TEST NAME}

Custom Regexp Matching Variables When Regexp Does No Match Them
    Check Test Case    ${TEST NAME}

Regexp Extensions Are Not Supported
    Check Test Case    ${TEST NAME}
    Creating Keyword Failed    1
    ...    Regexp extensions like \${x:(?x)re} are not supported
    ...    Regexp extensions are not allowed in embedded arguments.

Invalid Custom Regexp
    Check Test Case    ${TEST NAME}
    Creating Keyword Failed    2
    ...    Invalid \${x:(} Regexp
    ...    Compiling embedded arguments regexp failed: *
    ...    pattern=yes

Escaping Values Given As Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${name}, \${item} = User \\\${nonex} Selects \\\\ From Webshop
    Should Be Equal    ${tc.kws[2].name}    \${name}, \${item} = User \\ Selects \\ \\ From Webshop

Embedded Arguments Syntax Is Case Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    x Gets y From The z
    Should Be Equal    ${tc.kws[1].name}    x gets y from the z
    Should Be Equal    ${tc.kws[2].name}    x GETS y from the z
    Should Be Equal    ${tc.kws[3].name}    x gets y FROM THE z

Embedded Arguments Syntax is Space and Underscore Sensitive
    Check Test Case    Embedded Arguments Syntax is Space Sensitive
    Check Test Case    Embedded Arguments Syntax is Underscore Sensitive

Embedded Arguments In Resource File
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${ret} = embedded_args_in_uk_1.Juha Uses Resource File

Embedded Arguments In Resource File Used Explicitly
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    \${ret} = embedded_args_in_uk_1.peke uses resource file

Embedded And Positional Arguments Do Not Work Together
    Check Test Case    ${TEST NAME}

Keyword with embedded args cannot be used as "normal" keyword
    Check Test Case    ${TEST NAME}

Creating keyword with both normal and embedded arguments fails
    Creating Keyword Failed    0
    ...    Keyword with \${embedded} and normal args is invalid
    ...    Keyword cannot have both normal and embedded arguments.
    Check Test Case    ${TEST NAME}

Keyword matching multiple keywords in test case file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    foo+tc+bar
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    foo-tc-bar
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    foo+tc+bar+tc+zap

Keyword matching multiple keywords in one resource file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    foo+r1+bar
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    foo-r1-bar

Keyword matching multiple keywords in different resource files
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    foo-r1-bar
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    foo-r2-bar

Keyword matching multiple keywords in one and different resource files
    Check Test Case    ${TEST NAME}

*** Keywords ***
Creating Keyword Failed
    [Arguments]    ${index}    ${name}    ${error}    ${pattern}=
    Check Log Message    ${ERRORS.msgs[${index}]}
    ...    Creating user keyword '${name}' failed: ${error}    ERROR    pattern=${pattern}
