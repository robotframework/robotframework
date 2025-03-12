*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/non_main_threads_logging.robot
Resource        atest_resource.robot

*** Test Cases ***
Log messages from non-main threads should be ignored
    ${tc} =  Check Test Case  ${TESTNAME}
    Should Be Empty      ${tc[0].messages}
    Should Be Empty      ${tc[1].messages}
    Check Log Message    ${tc[2, 0]}          0
    Check Log Message    ${tc[2, 99]}         99
    Length Should Be     ${tc[3].messages}    100
    Check Log Message    ${tc[3, 0]}          0
    Check Log Message    ${tc[3, 99]}         99
    Length Should Be     ${tc[3].messages}    100
