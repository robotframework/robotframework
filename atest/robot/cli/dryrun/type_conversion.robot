*** Settings ***
Resource    atest_resource.robot

*** Test Cases ***
Annotations
    [Tags]    require-py3
    Run Tests    --dryrun    keywords/type_conversion/annotations.robot
    Should be equal    ${SUITE.status}    PASS

Keyword Decorator with Python 3
    [Tags]    require-py3
    Run Tests    --dryrun --exclude negative    keywords/type_conversion/keyword_decorator.robot
    Should be equal    ${SUITE.status}    PASS

Keyword Decorator with Python 2
    [Tags]    require-py2
    Run Tests    --dryrun --exclude negative --exclude require-py3    keywords/type_conversion/keyword_decorator.robot
    Should be equal    ${SUITE.status}    PASS
