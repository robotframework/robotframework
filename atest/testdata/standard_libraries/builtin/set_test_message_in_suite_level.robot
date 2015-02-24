*** Settings ***
Suite Setup       Set Test Message    This Is Illegal
Suite Teardown    Set Test Message    This is Also Illegal

*** Test Cases ***
Test
    No Operation
