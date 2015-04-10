*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  keywords/embedded_arguments_library_keywords.robot
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot

*** Test Cases ***
Embedded Arguments In Library Keyword Name
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  This is always executed
    Should Be Equal  ${tc.kws[0].name}  \${name}, \${book} = embedded_args_in_lk_1.User Peke Selects Advanced Python From Webshop
    Check Log Message  ${tc.kws[2].msgs[0]}  This is always executed
    Should Be Equal  ${tc.kws[2].name}  \${name}, \${book} = embedded_args_in_lk_1.User Juha selects Playboy from webshop

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    feature-works
    Check Log Message    ${tc.kws[1].msgs[0]}    test case-is *executed*
    Check Log Message    ${tc.kws[2].msgs[0]}    issue-is about to be done!

Embedded Arguments with BDD Prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    embedded_args_in_lk_1.Given user x selects y from webshop
    Should Be Equal    ${tc.kws[1].name}    embedded_args_in_lk_1.When user x selects y from webshop
    Should Be Equal    ${tc.kws[2].name}    \${x}, \${y} = embedded_args_in_lk_1.Then user x selects y from webshop

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    embedded_args_in_lk_1.User \${non existing} Selects \${variables} From Webshop

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

Embedded Arguments Syntax is Space and Underscore Sensitive
    Check Test Case    Embedded Arguments Syntax is Space Sensitive
    Check Test Case    Embedded Arguments Syntax is Underscore Sensitive

Keyword matching multiple keywords in library file
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    foo+lib+bar
    Check Log Message    ${tc.kws[1].msgs[0]}    foo-lib-bar
    Check Log Message    ${tc.kws[2].msgs[0]}    foo+lib+bar+lib+zap

Keyword matching multiple keywords in different library files
    Check Test Case    ${TEST NAME}

Embedded And Positional Arguments Do Not Work Together
    Check Test Case    ${TEST NAME}

Keyword with embedded args cannot be used as "normal" keyword
    Check Test Case    ${TEST NAME}

Embedded argument count must match accepted arguments
    Check Test Case    ${TESTNAME}
    ${msg} =    Catenate
    ...    Adding keyword 'Wrong \${number} Of Embedded \${args}' to library 'embedded_args_in_lk_1' failed:
    ...    Embedded argument count does not match number of accepted arguments.
    Check Log Message    ${ERRORS[0]}    ${msg}    ERROR

Optional Non-Embedded Args Are Okay
    Check Test Case    ${TESTNAME}

Star Args With Embedded Args Are Okay
    Check Test Case    ${TESTNAME}
