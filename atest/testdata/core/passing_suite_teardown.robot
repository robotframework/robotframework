*** Settings ***
Documentation     Passing suite teardown using base keyword.
Suite Teardown    Create File    ${TEARDOWN FILE}
Library           OperatingSystem

*** Variables ***
${TEARDOWN FILE}    %{TEMPDIR}/robot-suite-teardown-executed.txt

*** Test Cases ***
Test
    No Operation
