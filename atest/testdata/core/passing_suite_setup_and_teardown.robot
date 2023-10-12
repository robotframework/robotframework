*** Settings ***
Documentation     Passing suite setup and teardon using user keywords.
Suite Setup       My Setup
Suite Teardown    My Teardown
Library           OperatingSystem

*** Variables ***
${TEARDOWN FILE}    %{TEMPDIR}/robot-suite-teardown-executed.txt

*** Test Cases ***
Verify Suite Setup
    [Documentation]    PASS
    Should Be Equal    ${SUITE SETUP}    Suite Setup Executed

*** Keywords ***
My Setup
    Comment    Testing that suite setup can be also a user keyword
    My Keyword

My Teardown
    Comment    Testing that suite teardown can be also a user keyword
    No Operation
    Create File    ${TEARDOWN FILE}

My keyword
    Set Suite Variable    $SUITE SETUP    Suite Setup Executed
