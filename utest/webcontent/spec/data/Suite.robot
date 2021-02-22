*** Settings ***
Documentation   suite doc
Metadata        meta  data

*** Test Cases ***
Test
    [Documentation]  test doc
    [Tags]  tag1  tag2
    [Timeout]  1 second
    Sleep  0.1 seconds
    FOR  ${i}  IN RANGE  2
      my keyword  ${i}
    END

*** Keywords ***
my keyword
    [Arguments]  ${index}
    Log  index is ${index}

