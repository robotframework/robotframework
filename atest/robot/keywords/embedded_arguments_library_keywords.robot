*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  keywords/embedded_arguments_library_keywords.robot
Force Tags      regression  pybot
Resource        atest_resource.robot

*** Test Cases ***
Embedded Arguments In Library Keyword Name
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  This is always executed
    Should Be Equal  ${tc.kws[0].name}  \${name}, \${book} = embedded_args_in_lk_1.User \${user} Selects \${item} From Webshop
    Check Log Message  ${tc.kws[2].msgs[0]}  This is always executed
    Should Be Equal  ${tc.kws[2].name}  \${name}, \${book} = embedded_args_in_lk_1.User \${user} Selects \${item} From Webshop

Embedded And Positional Arguments Do Not Work Together
    Check Test Case    ${TEST NAME}

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    feature-works
    Check Log Message    ${tc.kws[1].msgs[0]}    test case-is *executed*
    Check Log Message    ${tc.kws[2].msgs[0]}    issue-is about to be done!

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].name}    embedded_args_in_lk_1.User \${user} Selects \${item} From Webshop

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
    ${tc} =    Check Test Case    ${TEST NAME}

Embedded Args Don't Match Keyword Args
    Check Test Case    ${TESTNAME}

Optional Non-Embedded Args Are Okay
    Check Test Case    ${TESTNAME}

Star Args With Embedded Args Are Okay
    Check Test Case    ${TESTNAME}
