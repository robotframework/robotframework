*** Settings ***
Resource          tidy_resource.robot
Suite Setup       Create Directory     ${TEMP}
Suite Teardown    Remove Directory     ${TEMP}    recursive=True
Test Template     Verify documentation formatting

*** Test Cases ***
Documentation in text file
    robot
    txt

Documentation in TSV file
    tsv

Documentation in HTML file
    html

*** Keywords ***
Verify documentation formatting
    [Arguments]    ${format}
    Run tidy and check result    --format=${format}    documentation.robot    expected=documentation_expected.${format}
