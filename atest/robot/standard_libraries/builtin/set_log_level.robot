*** Settings ***
Suite Setup       Run Tests    --log set_log_level_log.html    standard_libraries/builtin/set_log_level.robot
Resource          atest_resource.robot

*** Test Cases ***
Set Log Level
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}       Log level changed from INFO to TRACE.     DEBUG
    Check Log Message    ${tc[1, 1]}       This is logged                            TRACE
    Check Log Message    ${tc[2, 1]}       This is logged                            DEBUG
    Check Log Message    ${tc[3, 1]}       This is logged                            INFO
    Check Log Message    ${tc[4, 1]}       Log level changed from TRACE to DEBUG.    DEBUG
    Should Be Empty      ${tc[6].body}
    Check Log Message    ${tc[7, 0]}       This is logged                            DEBUG
    Check Log Message    ${tc[8, 0]}       This is logged                            INFO
    Should Be Empty      ${tc[9].body}
    Should Be Empty      ${tc[10].body}
    Should Be Empty      ${tc[11].body}
    Check Log Message    ${tc[12, 0]}      This is logged                            INFO
    Should Be Empty      ${tc[15].body}
    Check Log Message    ${tc[16, 0]}      This is logged                            ERROR
    Should Be Empty      ${tc[17].body}
    Should Be Empty      ${tc[18].body}
    Should Be Empty      ${tc[19].body}

Invalid Log Level Failure Is Catchable
    Check Test Case    ${TESTNAME}

Reset Log Level
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}       Log level changed from INFO to DEBUG.     DEBUG
    Check Log Message    ${tc[1, 0]}       This is logged                            INFO
    Check Log Message    ${tc[2, 0]}       This is logged                            DEBUG
    Should Be Empty      ${tc[3].body}
    Check Log Message    ${tc[4, 0]}       This is logged                            INFO
    Should Be Empty      ${tc[5].body}

Log Level Goes To HTML
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    KW Info to log
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    KW Trace to log
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    TC Info to log
    File Should Contain    ${OUTDIR}${/}set_log_level_log.html    TC Trace to log
