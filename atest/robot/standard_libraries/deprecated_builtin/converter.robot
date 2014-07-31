*** Setting ***
Suite Setup       Run Tests    ${EMPTY}   standard_libraries/deprecated_builtin/converter.txt
Force Tags        regression    jybot    pybot
Resource          atest_resource.txt

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

