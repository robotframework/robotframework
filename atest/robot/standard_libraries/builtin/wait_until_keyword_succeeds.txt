***Settings***
Resource       atest_resource.txt
Force Tags     jybot  pybot  regression
Suite Setup    Run Tests  ${EMPTY}  standard_libraries/builtin/wait_until_keyword_succeeds.txt
Test Template  Check Test Case

***Test Cases***
Fail Because Timeout exceeded                                   ${TEST NAME}
Pass with first Try                                             ${TEST NAME}
Pass With Some Medium Try                                       ${TEST NAME}
Pass With Last Possible Try                                     ${TEST NAME}
Pass With Returning Value Correctly                             ${TEST NAME}
Invalid Timeout Does Not Cause Uncatchable Failure              ${TEST NAME}
Invalid Retry Interval Does Not Cause Uncatchable Failure       ${TEST NAME}
Wait Until In User Keyword                                      ${TEST NAME}
Failing User Keyword with Wait Until                            ${TEST NAME}
Passing User Keyword with Wait Until                            ${TEST NAME}
Wait Until With Longer Test Timeout                             ${TEST NAME}
Wait Until With Shorter Test Timeout                            ${TEST NAME}
Wait Until With Longer Keyword Timeout                          ${TEST NAME}
Wait Until With Shorter Keyword Timeout                         ${TEST NAME}
Invalid Number Of Arguments Inside Wait Until Keyword Succeeds  ${TEST NAME}
Invalid Keyword Inside Wait Until Keyword Succeeds              ${TEST NAME}
Keyword Not Found Inside Wait Until Keyword Succeeds            ${TEST NAME}

Variable Values Should Not Be Visible As Keyword's Arguments
  [Template]  NONE
  ${tc} =  Check Test Case  Pass With First Try
  Check KW Arguments  ${tc.kws[0].kws[0]}  \${HELLO}
