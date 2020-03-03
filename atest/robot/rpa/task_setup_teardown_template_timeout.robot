*** Settings ***
Suite Setup      Run Tests    --loglevel DEBUG    rpa/task_setup_teardown_template_timeout.robot
Resource         atest_resource.robot

*** Test Cases ***
Defaults
    ${tc} =    Check Test Case    ${TESTNAME}
    Check timeout message    ${tc.setup.msgs[0]}       1 minute 10 seconds
    Check log message        ${tc.setup.msgs[1]}       Setup has an alias!
    Check timeout message    ${tc.kws[0].msgs[0]}      1 minute 10 seconds
    Check log message        ${tc.kws[0].msgs[1]}      Using default settings
    Check log message        ${tc.teardown.msgs[0]}    Also teardown has an alias!!
    Should be equal          ${tc.timeout}             1 minute 10 seconds

Override
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message        ${tc.setup.msgs[0]}       Overriding setup
    Check log message        ${tc.kws[0].msgs[0]}      Overriding settings
    Check log message        ${tc.teardown.msgs[0]}    Overriding teardown as well
    Should be equal          ${tc.timeout}             ${NONE}

Task timeout exceeded
    ${tc} =    Check Test Case    ${TESTNAME}
    Check timeout message    ${tc.kws[0].msgs[0]}      99 milliseconds
    Check log message        ${tc.kws[0].msgs[1]}      Task timeout 99 milliseconds exceeded.    FAIL

Invalid task timeout
    Check Test Case    ${TESTNAME}

Task aliases are included in setting recommendations
    Error In File
    ...    0    rpa/task_setup_teardown_template_timeout.robot    6
    ...    SEPARATOR=\n
    ...    Non-existing setting 'Tesk Setup'. Did you mean:
    ...    ${SPACE*4}Test Setup
    ...    ${SPACE*4}Task Setup

Task settings are not allowed in resource file
    [Template]    Validate invalid setting error
    1    2    Task Setup
    2    3    Task Teardown
    3    4    Task Template
    4    5    Task Timeout

*** Keywords ***
Check timeout message
    [Arguments]    ${msg}    ${timeout}
    Check log message    ${msg}    Task timeout ${timeout} active. * seconds left.    DEBUG    pattern=True

Validate invalid setting error
    [Arguments]    ${index}    ${lineno}    ${setting}
    Error In File
    ...    ${index}    rpa/resource_with_invalid_task_settings.robot    ${lineno}
    ...    Non-existing setting '${setting}'.
