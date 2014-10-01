*** Settings ***
Library  Library.py
Library  OperatingSystem
Suite Teardown  Sleep  ${TEARDOWN SLEEP}

*** Test Case ***
Test
  Create File  ${TESTSIGNALFILE}
  Timeout In UK
  No operation

Test 2
  No operation

*** Keywords ***
Timeout In UK
  [Timeout]  3 seconds
  Busy Sleep  2
  No operation

