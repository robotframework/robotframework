*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/executed_builtin_keywords.robot
Resource          atest_resource.robot

*** Test Cases ***
Import Library
    Check Test Case    ${TESTNAME}
    Syslog Should Contain    Imported library 'String' with arguments [ ]
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ value | 42 ]

Set Library Search Order
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[1].full_name}    Second.Parameters
    Should Be Equal    ${tc.kws[2].full_name}    First.Parameters
    Should Be Equal    ${tc.kws[4].full_name}    Dynamic.Parameters

Set Tags
    Check Test Tags    ${TESTNAME}    \${2}    \${var}    Tag0    Tag1    Tag2

Remove Tags
    Check Test Tags    ${TESTNAME}    Tag1    Tag3
