*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/test_template.robot
Resource          atest_resource.robot

*** Test Cases ***
Using Normal Keyword Is Not Possible With Template
    Check Test Case    ${TESTNAME}

Default Template
    Check Test Case    ${TESTNAME}

Continue On Failure
    Check Test Case    ${TESTNAME}

Overriding Default Template In Test
    Check Test Case    ${TESTNAME}

Overriding Default Template In Test With Empty Value
    Check Test Case    ${TESTNAME}

Overriding Default Template In Test With NONE Value
    Check Test Case    ${TESTNAME}

Template With Variables
    Check Test Case    ${TESTNAME}

Template With \@{EMPTY} Variable
    Check Test Case    ${TESTNAME}

Template With Variables And Keyword Name
    Check Test Case    ${TESTNAME}

Template With Variable And Assign Mark (=)
    Check Test Case    ${TESTNAME}

Named Arguments
    Check Test Case    ${TESTNAME}

Varargs
    Check Test Case    ${TESTNAME}

Empty Values
    Check Test Case    ${TESTNAME}

Template With FOR Loop
    Check Test Case    ${TESTNAME}

Template With FOR Loop Containing Variables
    Check Test Case    ${TESTNAME}

Template With FOR IN RANGE Loop
    Check Test Case    ${TESTNAME}

Nested FOR
    Check Test Case    ${TESTNAME}

Invalid FOR
    Check Test Case    ${TESTNAME}

Template With IF
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].status}            PASS
    Should Be Equal    ${tc.body[0].body[0].type}      IF
    Should Be Equal    ${tc.body[0].body[0].status}    NOT RUN
    Should Be Equal    ${tc.body[0].body[1].type}      ELSE IF
    Should Be Equal    ${tc.body[0].body[1].status}    NOT RUN
    Should Be Equal    ${tc.body[0].body[2].type}      ELSE
    Should Be Equal    ${tc.body[0].body[2].status}    PASS

Template With IF Failing
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].status}            FAIL
    Should Be Equal    ${tc.body[0].body[0].type}      IF
    Should Be Equal    ${tc.body[0].body[0].status}    FAIL
    Should Be Equal    ${tc.body[1].status}            FAIL
    Should Be Equal    ${tc.body[1].body[0].type}      IF
    Should Be Equal    ${tc.body[1].body[0].status}    NOT RUN
    Should Be Equal    ${tc.body[1].body[1].type}      ELSE IF
    Should Be Equal    ${tc.body[1].body[1].status}    FAIL
    Should Be Equal    ${tc.body[1].body[2].type}      ELSE
    Should Be Equal    ${tc.body[1].body[2].status}    NOT RUN

Invalid IF
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].status}            FAIL
    Should Be Equal    ${tc.body[0].body[0].type}      IF
    Should Be Equal    ${tc.body[0].body[0].status}    FAIL

FOR and IF
    Check Test Case    ${TESTNAME}

User Keywords Should Not Be Continued On Failure
    Check Test Case    ${TESTNAME}

Commented Rows With Test Template
    Check Test Case    ${TESTNAME}

Templates with Run Keyword
    Check Test Case    ${TESTNAME}

Templates with continuable failures
    Check Test Case    ${TESTNAME}

Templated test ends after test timeout
    Check Test Case    ${TESTNAME}

Templated test with for loop ends after test timeout
    Check Test Case    ${TESTNAME}

Templated test continues after keyword timeout
    Check Test Case    ${TESTNAME}

Templated test with for loop continues after keyword timeout
    Check Test Case    ${TESTNAME}

Templated test ends after syntax errors
    Check Test Case    ${TESTNAME}

Templated test continues after non-syntax errors
    Check Test Case    ${TESTNAME}

Templates and fatal errors
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
