*** Settings ***
Documentation    NO RIDE because it would clean-up formatting.
Suite Setup
Suite Teardown
Test Setup
Test Teardown

*** Test Cases ***
Empty default setup and teardown
    No Operation

Empty custom setup and teardown
    [Setup]
    No Operation
    [Teardown]
