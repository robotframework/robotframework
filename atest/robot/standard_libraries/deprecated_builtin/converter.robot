*** Setting ***
Suite Setup       Run Tests    ${EMPTY}   standard_libraries/deprecated_builtin/converter.robot
Force Tags        regression
Resource          atest_resource.robot

*** Test Case ***
Integer
    Check testcase    ${TEST NAME}

Float
    Check testcase    ${TEST NAME}

String
    Check testcase    ${TEST NAME}

Boolean
    Check testcase    ${TEST NAME}

List
    Check testcase    ${TEST NAME}
