*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/executed_builtin_keywords.robot
Resource          atest_resource.robot

*** Test Cases ***
Import Library
    Check Test Case    ${TESTNAME}
    Check Syslog Contains    Imported library 'String' with arguments [ ]
    Check Syslog Contains    Imported library 'ParameterLibrary' with arguments [ value | 42 ]

Set Library Search Order
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[1].name}    Second.Parameters
    Should Be Equal    ${tc.kws[2].name}    First.Parameters
    Should Be Equal    ${tc.kws[4].name}    Dynamic.Parameters
