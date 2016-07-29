*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keyword_if_keyword_passed_failed
Resource          atest_resource.robot

*** Test Case ***
Run Keyword If keyword Failed Can't Be Used In Suite Setup or Teardown
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${SUITE.suites[0].setup.msgs[0]}    Keyword 'Run Keyword If Keyword Failed' can only be used in keyword teardown.    FAIL
    Check Log Message    ${SUITE.suites[0].teardown.msgs[0]}    Keyword 'Run Keyword If Keyword Failed' can only be used in keyword teardown.    FAIL

Run Keyword If keyword Failed When Keyword Fails
    ${tc} =    Check Test Case    ${TEST NAME}
    Log Many  ${tc.kws[0].keywords}
    Should Be Equal    ${tc.kws[0].keywords.teardown.name}    BuiltIn.Run Keyword If Keyword Failed
    Should Be Equal    ${tc.kws[0].keywords.teardown.kws[0].name}    BuiltIn.Log
    Check Log Message    ${tc.kws[0].keywords.teardown.kws[0].msgs[0]}    Hello from keyword teardown!

Run Keyword If Keyword Failed When Keyword Does Not Fail
    ${tc} =    Check Test Case    ${TEST NAME}
