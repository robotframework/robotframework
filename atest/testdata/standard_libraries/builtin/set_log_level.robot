*** Variables ***
# Used to make arguments look different from actual printout in html
${TO LOG} =    to log

*** Test Cases ***
Set Log Level
    Set Log Level  TRACE
    Log  This is logged  TRACE
    Log  This is logged  DEBUG
    Log  This is logged  INFO
    ${old} =  Set Log Level  debug
    Should Be Equal  ${old}  TRACE
    Log  This is NOT logged  TRACE
    Log  This is logged  DEBUG
    Log  This is logged  INFO
    Set Log Level  Info
    Log  This is NOT logged  TRACE
    Log  This is NOT logged  DEBUG
    Log  This is logged  INFO
    ${old} =  Set Log Level  ErRoR
    Should Be Equal  ${old}  INFO
    Log  This is NOT logged  INFO
    Log  This is logged  ERROR
    Set Log Level  NONE
    Log  NOT logged
    Log  NOT logged  FAIL
    [Teardown]  Set Log Level  INFO

Invalid Log Level Failure Is Catchable
    Run Keyword And Expect Error  Invalid log level 'INVALID'  Set Log Level  INVALID

Log Level Goes To HTML
    Set Log Level  Trace
    Log    TC Trace ${to log}   Trace
    Log    TC Info ${to log}   Info
    logging kw


*** Keywords ***
logging kw
    Log    KW Trace ${to log}   Trace
    Log    KW Info ${to log}   Info
