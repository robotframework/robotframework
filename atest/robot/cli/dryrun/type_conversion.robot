*** Settings ***
Resource    atest_resource.robot

*** Test Cases ***
Annotations
    [Tags]    require-py3
    Run Tests    --dryrun    keywords/type_conversion/annotations.robot
    Should be equal    ${SUITE.status}    PASS

Keyword Decorator PASS tests
    Run Tests    --dryrun --exclude negative    keywords/type_conversion/keyword_decorator.robot
    Should be equal    ${SUITE.status}    PASS

Keyword Decorator FAIL tests
    ${result} =    Run Tests    --dryrun --include negative    keywords/type_conversion/keyword_decorator.robot
    Should be equal    ${SUITE.status}    FAIL
    ${testcases} =    Get tests from suite    ${SUITE}
    Length should be    ${testcases}    ${result.rc}    msg=Not all negative test cases failed.
