*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/background_logging.robot
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Test Case ***
Log main
    ${tc}=    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Foo    INFO

Log from Background
    ${tc}=   Check Test Case      ${TEST NAME}
    Check Log Message    ${tc.kws[2].msgs[1]}    Bar    INFO

Log from specific thread
    ${tc}=   Check Test Case      ${TEST NAME}
    Check Log Message    ${tc.kws[5].msgs[0]}    Huu    INFO
