*** Settings ***
Suite Setup       Run Tests    ${EMPTY}
...    standard_libraries/builtin/set_test_message.robot standard_libraries/builtin/set_test_message_in_suite_level.robot
Resource          atest_resource.robot

*** Test Cases ***
Set Message To Successful Test
    ${tc} =    Check Test Case    ${TEST NAME}    PASS    My Test Message
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test message to:\nMy Test Message

Reset Message
    Check Test Case    ${TEST NAME}    PASS    My Real Test Message

Append To Message
    ${tc} =    Check Test Case    ${TEST NAME}    PASS    My message is continued
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test message to:\nMy message
    Check Log Message    ${tc.kws[1].msgs[0]}    Set test message to:\nMy message is continued

Set Non-ASCII Message
    ${tc} =    Check Test Case    ${TEST NAME}    PASS    Hyvää yötä
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test message to:\nHyvää yötä

Set Multiline Message
    ${tc} =    Check Test Case    ${TEST NAME}    PASS    1\n2\n3
    Check Log Message    ${tc.kws[0].msgs[0]}    Set test message to:\n1\n2\n3

Set Non-String Message
    Check Test Case    ${TEST NAME}    PASS    42

Failure Resets Set Message
    Check Test Case    ${TEST NAME}

Set Message To Failed Test On Teardown
    Check Test Case    ${TEST NAME}

Append To Failure Message
    Check Test Case    ${TEST NAME}

Setting Message In Test Body After Continuable Failure Has No Effect
    Check Test Case    ${TEST NAME}

Setting Message In Teardown After Continuable Failure Works
    Check Test Case    ${TEST NAME}

Set Message In Body and Fail In Teardown
    Check Test Case    ${TEST NAME}

Set Message In Teardown And Fail Afterwards
    Check Test Case    ${TEST NAME}

Fail In Teardown And Set Message Afterwards
    Check Test Case    ${TEST NAME}

Set Message In Setup
    Check Test Case    ${TEST NAME}    PASS    Message set in setup

Check Message From Previous Test
    Check Test Case    ${TEST NAME}

Not Allowed In Suite Setup or Teardown
    ${error}=    Catenate    SEPARATOR=\n
    ...    Suite setup failed:
    ...    'Set Test Message' keyword cannot be used in suite setup or teardown.
    ...    ${EMPTY}
    ...    Also suite teardown failed:
    ...    'Set Test Message' keyword cannot be used in suite setup or teardown.
    Should Be Equal    ${SUITE.suites[1].message}    ${error}
