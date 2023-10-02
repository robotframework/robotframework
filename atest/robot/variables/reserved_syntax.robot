*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/reserved_syntax.robot
Resource          atest_resource.robot

*** Test Cases ***
Reserved Syntax \*{var}
    Check Test Case    ${TEST NAME}

Reserved With Variable Indise
    Check Test Case    ${TEST NAME}

There should Be A Warning About Using Reserved Syntax In Stderr
    Validate Reserved Warning    \*{var}                    0
    Validate Reserved Warning    \*{this_causes_warning}    1
    Validate Reserved Warning    \*{Hello, world!}          2

*** Keywords ***
Validate Reserved Warning
    [Arguments]    ${reserved}    ${index}
    ${message} =    Catenate
    ...    Syntax '${reserved}' is reserved for future use.
    ...    Please escape it like '\\${reserved}'.
    Check Log Message    ${ERRORS[${index}]}    ${message}    WARN
