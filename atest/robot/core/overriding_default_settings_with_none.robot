*** Settings ***
Suite Setup     Run Tests  --variable config:NONE  core/overriding_default_settings_with_none.robot
Resource        atest_resource.robot

*** Test Cases ***

Overriding Test Setup
    ${tc}=  Check Test Case  ${TESTNAME}
    Setup Should Not Be Defined  ${tc}

Overriding Test Setup from Command Line
    ${tc}=  Check Test Case  ${TESTNAME}
    Setup Should Not Be Defined  ${tc}

Overriding Test Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Teardown Should Not Be Defined  ${tc}

Overriding Test Teardown from Command Line
    ${tc}=  Check Test Case  ${TESTNAME}
    Teardown Should Not Be Defined  ${tc}

Overriding Test Template
    ${tc}=  Check Test Case  ${TESTNAME}
    Should Be Equal  ${tc.body[0].full_name}  BuiltIn.No Operation

Overriding Test Timeout
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.body[0].msgs[0]}  Slept 123 milliseconds.

Overriding Test Timeout from Command Line
    ${tc}=  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.body[0].msgs[0]}  Slept 123 milliseconds.

Overriding Default Tags
    ${tc}=  Check Test Case  ${TESTNAME}
    Should Be Empty  ${tc.tags}

Overriding Default Tags from Command Line
    ${tc}=  Check Test Case  ${TESTNAME}
    Should Be Empty  ${tc.tags}

Overriding Is Case Insensitive
    ${tc}=  Check Test Case  ${TESTNAME}
    Setup Should Not Be Defined  ${tc}
    Teardown Should Not Be Defined  ${tc}
    Should Be Equal  ${tc.body[0].full_name}  BuiltIn.No Operation
    Should Be Empty  ${tc.tags}
