*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/async_dynamic_lib.robot
Resource         atest_resource.robot

*** Test Cases ***
Dynamic async kw works
    Check Test Case    ${TESTNAME}
