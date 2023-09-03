*** Settings ***
Resource    atest_resource.robot

*** Test Cases ***
Annotations
    Run Tests    --dryrun    keywords/type_conversion/annotations.robot
    Should be equal    ${SUITE.status}    PASS

Keyword Decorator
    Run Tests    --dryrun --exclude negative    keywords/type_conversion/keyword_decorator.robot
    Should be equal    ${SUITE.status}    PASS

Custom converters
    Run Tests    --dryrun --exclude no-dry-run    keywords/type_conversion/custom_converters.robot
    Should be equal    ${SUITE.status}    PASS
