*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/evaluate.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Evaluate
    Check Test Case    ${TEST NAME}

Evaluate With Modules
    Check Test Case    ${TEST NAME}

Evaluate With Namespace
    Check Test Case    ${TEST NAME}

Evaluate Empty
    Check Test Case    ${TEST NAME}

Evaluate Nonstring
    Check Test Case    ${TEST NAME}
