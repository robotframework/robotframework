*** Settings ***
Library  Library.py
Library  OperatingSystem
Suite Teardown  Sleep  ${TEARDOWN SLEEP}

*** Test Case ***
Test
    Create File  ${TESTSIGNALFILE}
    Swallow exception
    Fail  Should not be executed

Test 2
    Fail  Should not be executed

