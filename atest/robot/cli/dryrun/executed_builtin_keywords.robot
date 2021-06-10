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
    Should Be Equal    ${tc.kws[1].name}    Second.Parameters
    Should Be Equal    ${tc.kws[2].name}    First.Parameters
    Should Be Equal    ${tc.kws[4].name}    Dynamic.Parameters

Set Tags
    ${tc} =    Check Test Case    ${TESTNAME}
    List Should Contain Value    ${tc.tags}    Tag0
    List Should Contain Value    ${tc.tags}    Tag1
    List Should Contain Value   ${tc.tags}    Tag2
    List Should Contain Value   ${tc.tags}   Tag3

Remove Tags
    ${tc} =    Check Test Case    ${TESTNAME}
    List Should Contain Value   ${tc.tags}    Tag1
    List Should Not Contain Value   ${tc.tags}    Tag2
    List Should Contain Value   ${tc.tags}   Tag3


