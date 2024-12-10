*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/executed_builtin_keywords.robot
Resource          atest_resource.robot

*** Test Cases ***
Import Library
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Import Library    args=String
    Syslog Should Contain    Imported library 'String' with arguments [ ]
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ value | 42 ]

Import Resource
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Import Resource    args=\${RESOURCE}
    ${resource} =    Normalize Path    ${DATADIR}/cli/dryrun/resource.robot
    Syslog Should Contain    Imported resource file '${resource}' (6 keywords).

Set Library Search Order
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc[0]}    BuiltIn.Set Library Search Order    args=Second
    Should Be Equal    ${tc[1].full_name}    Second.Parameters
    Should Be Equal    ${tc[2].full_name}    First.Parameters
    Should Be Equal    ${tc[4].full_name}    Dynamic.Parameters

Set Tags
    ${tc} =    Check Test Tags    ${TESTNAME}    \${2}    \${var}    Tag0    Tag1    Tag2
    Check Keyword Data    ${tc[0]}    BuiltIn.Set Tags    args=Tag1, Tag2, \${var}, \${2}

Remove Tags
    ${tc} =    Check Test Tags    ${TESTNAME}    Tag1    Tag3
    Check Keyword Data    ${tc[0]}    BuiltIn.Remove Tags    args=Tag2, \${var}
