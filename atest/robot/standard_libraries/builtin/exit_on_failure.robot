*** Settings ***
Resource        atest_resource.robot

*** Test Cases ***
Wait Until Keyword Succeeds
    Run "Wait Until Keyword Succeeds" test which should fail immediately to Exit On Failure
    Check Rest of the tests have failed due the Exit On Failure

Run Keyword And Expect Error
    Run "run keyword and expect error" test which should fail immediately to Exit On Failure
    Check Rest of the tests have failed due the Exit On Failure

Run Keyword And Ignore Error
    Run "run keyword and ignore error" test which should fail immediately to Exit On Failure
    Check Rest of the tests have failed due the Exit On Failure

*** Keywords ***
Run "${keyword name}" test Which Should Fail Immediately to Exit On Failure
    Run Tests  --test "${keyword name}" --test "failing test case"  standard_libraries/builtin/exit_on_failure.robot
    Check Test Case  ${keyword name}

Check Rest of the tests have failed due the Exit On Failure
    Check Test Case  Failing Test Case

