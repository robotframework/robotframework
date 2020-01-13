*** Settings ***
Resource          tidy_resource.robot
Suite Setup       Create Directory     ${TEMP}
Suite Teardown    Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***
Documentation in text file
    Run tidy and check result    ${EMPTY}  documentation.robot    expected=documentation_expected.robot
