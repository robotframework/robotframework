*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  keywords/embedded_arguments.robot
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot

*** Test Cases ***
Embedded Arguments In User Keyword Name
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  This is always executed
    Should Be Equal  ${tc.kws[0].name}  \${name}, \${book} = User Peke Selects Advanced Python From Webshop
    Check Log Message  ${tc.kws[2].kws[0].msgs[0]}  This is always executed
    Should Be Equal  ${tc.kws[2].name}  \${name}, \${book} = User Juha Selects Playboy From Webshop

Embedded And Positional Arguments Do Not Work Together
    Check Test Case  ${TEST NAME}

Complex Embedded Arguments
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  feature-works
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  test case-is *executed*
    Check Log Message  ${tc.kws[2].kws[0].msgs[0]}  issue-is about to be done!

Argument Namespaces with Embedded Arguments
    Check Test Case  ${TEST NAME}

Embedded Arguments as Variables
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  \${name}, \${item} = User \${42} Selects \${EMPTY} From Webshop
    Should Be Equal  ${tc.kws[2].name}  \${name}, \${item} = User \${name} Selects \${SPACE * 10} From Webshop

Non-Existing Variable in Embedded Arguments
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  User \${non existing} Selects \${variables} From Webshop

Non-Existing Variable in Embedded Arguments and Positional Arguments
    Check Test Case  ${TEST NAME}

Non-Existing Variable in Embedded Arguments and in Positional Arguments
    Check Test Case  ${TEST NAME}

Custom Embedded Argument Regexp
    Check Test Case  ${TEST NAME}

Custom Regexp With Curly Braces
    Check Test Case  ${TEST NAME}

Custom Regexp With Escape Chars
    Check Test Case  ${TEST NAME}

Grouping Custom Regexp
    Check Test Case  ${TEST NAME}

Custom Regexp Matching Variables
    Check Test Case  ${TEST NAME}

Custom Regexp Matching Variables When Regexp Does No Match Them
    Check Test Case  ${TEST NAME}

Regexp Extensions Are Not Supported
    Check Log Message  ${ERRORS.msgs[0]}  Creating user keyword 'Regexp extensions like \${x:(?x)re} are not supported' failed: Regexp extensions are not allowed in embedded arguments.  ERROR

Invalid Custom Regexp
    Check Log Message  ${ERRORS.msgs[1]}  Creating user keyword 'Invalid \${x:(} Regexp' failed: Compiling embedded arguments regexp failed: *  ERROR  pattern=yes

Escaping Values Given As Embedded Arguments
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  \${name}, \${item} = User \\\${nonex} Selects \\\\ From Webshop
    Should Be Equal  ${tc.kws[2].name}  \${name}, \${item} = User \\ Selects \\ \\ From Webshop

Embedded Arguments Syntax Is Case Insensitive
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  x Gets y From The z
    Should Be Equal  ${tc.kws[1].name}  x gets y from the z
    Should Be Equal  ${tc.kws[2].name}  x GETS y from the z
    Should Be Equal  ${tc.kws[3].name}  x gets y FROM THE z

Embedded Arguments Syntax is Space and Underscore Sensitive
    Check Test Case  Embedded Arguments Syntax is Space Sensitive
    Check Test Case  Embedded Arguments Syntax is Underscore Sensitive

Embedded Arguments In Resource File
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  \${ret} = embedded_args_in_uk_1.Juha Uses Resource File

Embedded Arguments In Resource File Used Explicitly
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  \${ret} = embedded_args_in_uk_1.peke uses resource file

Keyword with normal arguments cannot have embedded arguments
    Check Test Case  ${TEST NAME}

Keyword with embedded args can be used as "normal" keyword
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  This is always executed

Keyword matching multiple keywords in test case file
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  foo+tc+bar
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  foo-tc-bar
    Check Log Message  ${tc.kws[2].kws[0].msgs[0]}  foo+tc+bar+tc+zap

Keyword matching multiple keywords in one resource file
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  foo+r1+bar
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  foo-r1-bar

Keyword matching multiple keywords in different resource files
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].kws[0].msgs[0]}  foo-r1-bar
    Check Log Message  ${tc.kws[1].kws[0].msgs[0]}  foo-r2-bar

Keyword matching multiple keywords in one and different resource files
    ${tc} =  Check Test Case  ${TEST NAME}

