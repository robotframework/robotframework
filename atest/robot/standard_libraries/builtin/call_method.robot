*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/call_method.robot
Force Tags      regression
Default Tags    jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***

Call Method
    Check Test Case  ${TEST NAME}

Call Method Returns
    Check Test Case  ${TEST NAME}

Called Method Fails
    Check Test Case  ${TEST NAME}

Call Method With Kwargs
    Check Test Case  ${TEST NAME}

Equals in non-kwargs must be escaped
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
