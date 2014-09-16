*** Settings ***
Suite Setup     Run Tests  --log set_log_level_log.html  standard_libraries/builtin/set_log_level.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Set Log Level
    ${tc} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${tc.kws[1].msgs[1]}  This is logged  TRACE
    Check Log Message  ${tc.kws[2].msgs[1]}  This is logged  DEBUG
    Check Log Message  ${tc.kws[3].msgs[1]}  This is logged  INFO
    Should Be Empty  ${tc.kws[6].msgs}
    Check Log Message  ${tc.kws[7].msgs[0]}  This is logged  DEBUG
    Check Log Message  ${tc.kws[8].msgs[0]}  This is logged  INFO
    Should Be Empty  ${tc.kws[10].msgs}
    Should Be Empty  ${tc.kws[11].msgs}
    Check Log Message  ${tc.kws[12].msgs[0]}  This is logged  INFO
    Should Be Empty  ${tc.kws[15].msgs}
    Check Log Message  ${tc.kws[16].msgs[0]}  This is logged  ERROR
    Should Be Empty  ${tc.kws[18].msgs}
    Should Be Empty  ${tc.kws[19].msgs}

Invalid Log Level Failure Is Catchable
    Check Test Case  ${TESTNAME}

Log Level Goes To HTML
    Check File Contains    ${OUTDIR}${/}set_log_level_log.html    KW Info to log
    Check File Contains    ${OUTDIR}${/}set_log_level_log.html    KW Trace to log
    Check File Contains    ${OUTDIR}${/}set_log_level_log.html    TC Info to log
    Check File Contains    ${OUTDIR}${/}set_log_level_log.html    TC Trace to log