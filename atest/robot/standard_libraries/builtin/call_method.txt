*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/call_method.txt
Force Tags      regression
Default Tags    jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***

Call Method
    Check Test Case  ${TEST NAME}

Call Method Returns
    Check Test Case  ${TEST NAME}

Call Method From Module
    Check Test Case  ${TEST NAME}

Call Non Existing Method
    Check Test Case  ${TEST NAME}

Call Java Method
    [Tags]  jybot
    Check Test Case  ${TEST NAME}

Call Non Existing Java Method
    [Tags]  jybot
    Check Test Case  ${TEST NAME}
