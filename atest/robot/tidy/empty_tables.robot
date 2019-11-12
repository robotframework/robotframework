*** Settings ***
Resource          tidy_resource.robot
Suite Setup       Create Directory     ${TEMP}
Suite Teardown    Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***
Empty test case file
    Run tidy and check result    ${EMPTY}    testsuite_with_empty_tables.robot

Empty resource file
    Run tidy and check result    ${EMPTY}    resource_with_empty_tables.robot
