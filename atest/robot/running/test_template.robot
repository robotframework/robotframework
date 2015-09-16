*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  running/test_template.robot
Resource        atest_resource.robot

*** Test Cases ***
Test Using Normal Keyword Is Not Possible With Template
    Check Test Case  ${TESTNAME}

Test Default Template
    Check Test Case  ${TESTNAME}

Test Continue On Failure
    Check Test Case  ${TESTNAME}

Test Overriding Default Template In Test
    Check Test Case  ${TESTNAME}

Test Overriding Default Template In Test With Empty Value
    Check Test Case  ${TESTNAME}

Test Overriding Default Template In Test With NONE Value
    Check Test Case  ${TESTNAME}

Test Template With Variables
    Check Test Case  ${TESTNAME}

Test Template With @{EMPTY} Variable
    Check Test Case  ${TESTNAME}

Test Template With Variables And Keyword Name
    Check Test Case  ${TESTNAME}

Test Template With Variable And Assign Mark (=)
    Check Test Case  ${TESTNAME}

Test Named Arguments
    Check Test Case  ${TESTNAME}

Test Varargs
    Check Test Case  ${TESTNAME}

Test Empty Values
    Check Test Case  ${TESTNAME}

Test Template With FOR Loop
    Check Test Case  ${TESTNAME}

Test Template With FOR Loop Containing Variables
    Check Test Case  ${TESTNAME}

Test Template With FOR IN RANGE Loop
    Check Test Case  ${TESTNAME}

Test User Keywords Should Not Be Continued On Failure
    Check Test Case  ${TESTNAME}

Commented Rows With Test Template
    Check Test Case  ${TESTNAME}

Templates with Run Keyword
    Check Test Case  ${TESTNAME}

Templates with continuable failures
    Check Test Case  ${TESTNAME}

Templates and timeouts
    Check Test Case  ${TESTNAME}

Templates, timeouts, and for loops
    Check Test Case  ${TESTNAME}

Templated test ends after syntax errors
    Check Test Case  ${TESTNAME}

Templated test continues after variable error
    Check Test Case  ${TESTNAME}

Templates and fatal errors
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2
