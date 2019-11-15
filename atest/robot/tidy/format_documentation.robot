*** Settings ***
Resource          tidy_resource.robot
Suite Setup       Create Directory     ${TEMP}
Suite Teardown    Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***
Documentation in text file
    Verify documentation formatting    robot

*** Keywords ***
Verify documentation formatting
    [Arguments]    ${format}
    Run tidy and check result    --format=${format}    documentation.robot    expected=documentation_expected.${format}
