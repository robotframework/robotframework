*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/keyword_decorator_with_wraps.robot
Resource         atest_resource.robot

*** Test Cases ***
Keyword Decorator With Wraps
    Check Test Case    ${TESTNAME}

Keyword Decorator With Wraps Mismatched Type
    Check Test Case    ${TESTNAME}
