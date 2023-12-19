*** Settings ***
Suite Setup       Run Tests    --log set_log_level_log.html    standard_libraries/builtin/set_log_level.robot
Resource          atest_resource.robot

*** Test Cases ***
Set Log Level
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Log level changed from INFO to TRACE.    DEBUG
    Check Log Message    ${tc.kws[1].msgs[1]}    This is logged    TRACE
    Check Log Message    ${tc.kws[2].msgs[1]}    This is logged    DEBUG
    Check Log Message    ${tc.kws[3].msgs[1]}    This is logged    INFO
    Check Log Message    ${tc.kws[4].msgs[1]}    Log level changed from TRACE to DEBUG.    DEBUG
    Should Be Empty      ${tc.kws[6].msgs}
    Check Log Message    ${tc.kws[7].msgs[0]}    This is logged    DEBUG
    Check Log Message    ${tc.kws[8].msgs[0]}    This is logged    INFO
    Should Be Empty      ${tc.kws[9].msgs}
    Should Be Empty      ${tc.kws[10].msgs}
    Should Be Empty      ${tc.kws[11].msgs}
    Check Log Message    ${tc.kws[12].msgs[0]}    This is logged    INFO
    Should Be Empty      ${tc.kws[15].msgs}
    Check Log Message    ${tc.kws[16].msgs[0]}    This is logged    ERROR
    Should Be Empty      ${tc.kws[17].msgs}
    Should Be Empty      ${tc.kws[18].msgs}
    Should Be Empty      ${tc.kws[19].msgs}

Invalid Log Level Failure Is Catchable
    Check Test Case    ${TESTNAME}

Reset Log Level
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Log level changed from INFO to DEBUG.    DEBUG
    Check Log Message    ${tc.kws[1].msgs[0]}    This is logged    INFO
    Check Log Message    ${tc.kws[2].msgs[0]}    This is logged    DEBUG
    Should Be Empty      ${tc.kws[3].msgs}
    Check Log Message    ${tc.kws[4].msgs[0]}    This is logged    INFO
    Should Be Empty      ${tc.kws[5].msgs}

Log Level Goes To HTML
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    KW Info to log
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    KW Trace to log
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    TC Info to log
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    TC Trace to log
