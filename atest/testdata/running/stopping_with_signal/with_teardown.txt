*** Settings ***
Library  Library.py
Library  OperatingSystem
Suite Teardown  My Suite Teardown

*** Test Case ***
Test
  Create File  ${TESTSIGNALFILE}
  Busy Sleep  2
  No Operation
  [teardown]  Log  Logging Test Case Teardown

Test 2
  No Operation

*** Keywords ***
My Suite Teardown
    Log  Logging Suite Teardown
    Sleep  ${TEARDOWN SLEEP}
