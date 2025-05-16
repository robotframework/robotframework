*** Settings ***
Resource    atest_resource.robot

*** Test Cases ***
Annotations
    # Exclude test requiring Python 3.14 unconditionally to avoid a failure with
    # older versions. It can be included once Python 3.14 is our minimum versoin.
    Run Tests    --dryrun --exclude require-py3.14    keywords/type_conversion/annotations.robot
    Should be equal    ${SUITE.status}    PASS

Keyword Decorator
    Run Tests    --dryrun --exclude negative    keywords/type_conversion/keyword_decorator.robot
    Should be equal    ${SUITE.status}    PASS

Custom converters
    Run Tests    --dryrun --exclude no-dry-run    keywords/type_conversion/custom_converters.robot
    Should be equal    ${SUITE.status}    PASS
