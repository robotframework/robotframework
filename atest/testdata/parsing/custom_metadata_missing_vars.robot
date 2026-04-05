*** Settings ***
Documentation     Test data for missing variables in custom metadata.

*** Test Cases ***
Missing Variables Test
    [Documentation]    Test custom metadata with missing variables
    [Missing]         ${MISSING_VAR} not defined
    [Partial]         Known: ${TEMPDIR}, Unknown: ${UNKNOWN_VAR}
    [Empty List]      @{NON_EXISTENT_LIST}
    [Empty Dict]      &{NON_EXISTENT_DICT}
    Log    Missing variables test
