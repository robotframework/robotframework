*** Settings ***
Suite Setup      Run Tests    --dryrun    cli/dryrun/kwargs.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Normal and kwargs
    Check Test Case    ${TESTNAME}

Varargs and kwargs
    Check Test Case    ${TESTNAME}

Kwargs
    Check Test Case    ${TESTNAME}

Invalid kwargs
    Check Test Case    ${TESTNAME}
