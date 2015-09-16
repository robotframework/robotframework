*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  variables/environment_variables.robot
Resource        atest_resource.robot

*** Test Cases ***
Environment Variables In Keyword Argument
    Check Test Case  ${TESTNAME}

Java System Properties Can Be Used
    [Tags]  require-jython
    Check Test Case  ${TESTNAME}

Non-ASCII Environment Variable
    Check Test Case  ${TESTNAME}

Environment Variable With Backslashes
    Check Test Case  ${TESTNAME}

Environment Variable With Internal Variables
    Check Test Case  ${TESTNAME}

Non-Existing Environment Variable
    Check Test Case  ${TESTNAME}

Environment Variables Are Case Sensitive Except On Windows
    Run Keyword If  '${:}' == ':'  Check Test Case  Environment Variables Are Case Sensitive
    Run Keyword Unless  '${:}' == ':'  Check Test Case  Environment Variables Are Not Case Sensitive On Windows

Environment Variables Are Space Sensitive
    Check Test Case  ${TEST_NAME} 1
    Check Test Case  ${TEST_NAME} 2

Environment Variables Are Underscore Sensitive
    Check Test Case  ${TEST_NAME}

Environment Variables In Variable Table
    Check Test Case  ${TESTNAME}

Environment Variables In Settings Table
    Check Test Case  ${TESTNAME}
    Should Be Equal  ${SUITE.doc}  %{PATH} used in suite documentation
    Should Be Equal  ${SUITE.metadata['PATH']}  %{PATH}
    Should Contain  ${SUITE.doc}  ${:}  Make sure %{PATH} is ...
    Should Contain  ${SUITE.metadata['PATH']}  ${:}  ... actually resolved

Environment Variables In Test Metadata
    ${tc} =  Check Test Case  ${TESTNAME}
    Should Be Equal  ${tc.doc}  Env var value in a test doc

Environment Variables In User Keyword Metadata
    ${tc} =  Check Test Case  ${TESTNAME}
    Should Be Equal  ${tc.kws[0].doc}  Env var value in a uk doc

Escaping Environment Variables
    Check Test Case  ${TESTNAME}

Empty Environment Variable
    Check Test Case  ${TESTNAME}
