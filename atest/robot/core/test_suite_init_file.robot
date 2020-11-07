*** Settings ***
Suite Setup      My Setup
Resource         atest_resource.robot

*** Variables ***
${suite}                   These three variables...
${subsuite_with_init}      ...are set in...
${subsuite_without_init}   ...'My Setup'.

*** Test Cases ***
Suite Name
    Should Be Equal   ${suite.name}   Test Suite Dir With Init File
    Should Be Equal   ${subsuite_with_init.name}   Sub Suite With Init File
    Should Be Equal   ${subsuite_without_init.name}   Sub Suite Without Init File

Suite Documentation
    [Documentation]   Setting and not setting documentation for a suite file and setting doc when there's not suite file.
    Should Be Equal   ${suite.doc}   Setting metadata for test suite directory
    Should Be Equal   ${subsuite_with_init.doc}   ${EMPTY}
    Should Be Equal   ${subsuite_without_init.doc}   ${EMPTY}

Suite Setup
    [Documentation]   Setting and not setting setup using suite file
    Check Log Message   ${suite.setup.kws[0].msgs[0]}   Setup of test suite directory
    Setup Should Not Be Defined   ${subsuite_with_init}
    Setup Should Not Be Defined   ${subsuite_without_init}

Suite Teardown
    [Documentation]   Setting and not setting teardown using suite file
    Check Log Message   ${suite.teardown.kws[1].msgs[0]}   Teardown of test suite directory
    Check Log Message   ${subsuite_with_init.teardown.kws[1].msgs[0]}   Teardown of sub test suite directory
    Teardown Should Not Be Defined   ${subsuite_without_init}

Invalid Suite Setting
    Error In File    0    core/test_suite_dir_with_init_file/__init__.robot    10
    ...    Non-existing setting 'Invalid'.
    Error In File    3    core/test_suite_dir_with_init_file/sub_suite_with_init_file/__INIT__.robot    7
    ...    Non-existing setting 'Megadata'. Did you mean:\n${SPACE*4}Metadata

Default Tags and Test Template are not allowed in init files
    Error In File    1    core/test_suite_dir_with_init_file/__init__.robot    11
    ...    Setting 'Default Tags' is not allowed in suite initialization file.
    Error In File    2    core/test_suite_dir_with_init_file/__init__.robot    12
    ...    Setting 'Test Template' is not allowed in suite initialization file.

Test Tags
    [Documentation]   Settings tags for tests using Force and Default Tags in different suite levels and also [Tags] in tests
    Check Test Tags   TC1 No Metadata   suite force   test default   test force
    Check Test Tags   TC1 Tags   suite force   test force   test tag 1   test tag 2
    Check Test Tags   TC2 No Metadata   suite force
    Check Test Tags   TC2 Tags   suite force
    Check Test Tags   S1TC1 No Metadata   sub suite force   suite force   test default   test force
    # Following two steps are for issue 152
    Check Test Tags   S1TC1 Fixture   sub suite force   suite force   test default   test force
    Check Test Tags   S1TC1 Timeout   sub suite force   suite force   test default   test force
    Check Test Tags   S1TC1 Tags   sub suite force   suite force   test force   test tag 1   test tag 2
    Check Test Tags   S1TC2 No Metadata   sub suite force   suite force
    Check Test Tags   S1TC2 Tags   sub suite force   suite force   t1   t2   t3   t4   t5
    Check Test Tags   S2TC1 No Metadata   suite force   test default   test force
    Check Test Tags   S2TC1 Tags   suite force   test force   test tag 1   test tag 2   test tag 3
    Check Test Tags   S2TC2 No Metadata   suite force
    Check Test Tags   S2TC2 Tags   suite force

Test Fixture
    [Documentation]   Settings setup and teardown for tests using Test Setup/Teardown in different suite levels and also [Setup] and [Teardown] in tests
    Check Test Fixture   TC1 No Metadata   Default setup from test file   Default teardown from test file
    Check Test Fixture   TC1 Fixture   Setup defined in test   Teardown defined in test
    Check Test Fixture   TC2 No Metadata   Default setup from suite file   Default teardown from suite file
    Check Test Fixture   TC2 Fixture   Setup defined in test   Teardown defined in test
    Check Test Fixture   S1TC1 No Metadata   Default setup from test file   Default teardown from test file
    Check Test Fixture   S1TC1 Fixture   Setup defined in test   Teardown defined in test
    Check Test Fixture   S1TC2 No Metadata   Default setup from sub suite file   Default teardown from suite file
    # Following step is for issue 152
    Check Test Fixture   S1TC2 Tags   Default setup from sub suite file   Default teardown from suite file
    Check Test Fixture   S1TC2 Fixture   Setup defined in test   Teardown defined in test
    Check Test Fixture   S2TC1 No Metadata   Default setup from test file   Default teardown from test file
    Check Test Fixture   S1TC2 Fixture   Setup defined in test   Teardown defined in test
    Check Test Fixture   S2TC2 No Metadata   Default setup from suite file   Default teardown from suite file
    Check Test Fixture   S2TC2 Fixture   Setup defined in test   Teardown defined in test

Test Timeout
    [Documentation]   Setting timeout for tests using Test Timeout in different suite levels and also [Timeout] in tests
    Check Test Timeout   TC1 No Metadata   1 hour 2 minutes 3 seconds
    Check Test Timeout   TC1 Timeout   100 milliseconds
    Check Test Timeout   TC2 No Metadata   13 days 6 hours 50 minutes
    Check Test Timeout   TC2 Timeout   1 hour
    Check Test Timeout   S1TC1 No Metadata   4 hours 5 minutes 6 seconds
    Check Test Timeout   S1TC1 Timeout   101 milliseconds
    Check Test Timeout   S1TC2 No Metadata   1 minute 52 seconds
    # Following step is for issue 152
    Check Test Timeout   S1TC2 Tags   1 minute 52 seconds
    Check Test Timeout   S1TC2 Timeout   1 day
    Check Test Timeout   S2TC1 No Metadata   7 hours 8 minutes 9 seconds
    Check Test Timeout   S2TC1 Timeout   99 milliseconds
    Check Test Timeout   S2TC2 No Metadata   13 days 6 hours 50 minutes
    Check Test Timeout   S2TC2 Timeout   1 day

*** Keywords ***
My Setup
    Run Tests   ${EMPTY}   core/test_suite_dir_with_init_file
    ${suite} =   Get Test Suite   Test Suite Dir With Init File
    ${subsuite_with_init} =   Get Test Suite   Sub Suite With Init File
    ${subsuite_without_init} =   Get Test Suite   Sub Suite Without Init File
    Set Suite Variable   $SUITE
    Set Suite Variable   $SUBSUITE_WITH_INIT
    Set Suite Variable   $SUBSUITE_WITHOUT_INIT

Check Test Fixture
    [Arguments]   ${test_name}   ${setup_msg}   ${teardown_msg}
    ${test} =   Check Test Case   ${test_name}
    Check Log Message   ${test.setup.messages[0]}   ${setup_msg}
    Check Log Message   ${test.teardown.messages[0]}   ${teardown_msg}

Check Test Timeout
    [Arguments]   ${test_name}   ${timeout}
    ${test} =   Check Test Case   ${test_name}
    Should Be Equal   ${test.timeout}   ${timeout}
