*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  keywords/embedded_arguments_library_keywords.robot
Resource        atest_resource.robot

*** Test Cases ***
Embedded Arguments In Library Keyword Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}    This is always executed
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_lk_1.User Peke Selects Advanced Python From Webshop    \${name}, \${book}
    Check Log Message  ${tc.kws[2].msgs[0]}    This is always executed
    Check Keyword Data    ${tc.kws[2]}    embedded_args_in_lk_1.User Juha selects Playboy from webshop    \${name}, \${book}

Complex Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    feature-works
    Check Log Message    ${tc.kws[1].msgs[0]}    test case-is *executed*
    Check Log Message    ${tc.kws[2].msgs[0]}    issue-is about to be done!

Embedded Arguments with BDD Prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_lk_1.Given user x selects y from webshop
    Check Keyword Data    ${tc.kws[1]}    embedded_args_in_lk_1.When user x selects y from webshop
    Check Keyword Data    ${tc.kws[2]}    embedded_args_in_lk_1.Then user x selects y from webshop    \${x}, \${y}

Argument Namespaces with Embedded Arguments
    Check Test Case    ${TEST NAME}

Embedded Arguments as Variables
    ${tc} =    Check Test Case    ${TEST NAME}

Non-Existing Variable in Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    embedded_args_in_lk_1.User \${non existing} Selects \${variables} From Webshop

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

Embedded Arguments Syntax is Space Sensitive
    Check Test Case    ${TEST NAME}

Embedded Arguments Syntax is Underscore Sensitive
    Check Test Case    ${TEST NAME}

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
    ...    Adding keyword 'Wrong \${number} of embedded \${args}' to library 'embedded_args_in_lk_1' failed:
    ...    Embedded argument count does not match number of accepted arguments.
    Check Log Message    ${ERRORS[0]}    ${msg}    ERROR

Optional Non-Embedded Args Are Okay
    Check Test Case    ${TESTNAME}

Star Args With Embedded Args Are Okay
    Check Test Case    ${TESTNAME}

Same name with different regexp works
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    a car
    Check Log Message    ${tc.kws[1].msgs[0]}    a dog
    Check Log Message    ${tc.kws[2].msgs[0]}    a cow

Same name with different regexp matching multiple fails
    Check Test Case    ${TEST NAME}

Same name with same regexp fails
    Check Test Case    ${TEST NAME}
