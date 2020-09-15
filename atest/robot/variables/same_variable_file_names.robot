*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  variables/same_variable_file_names
Resource        atest_resource.robot

*** Variables ***
${6 TESTS}    6 tests, 6 passed, 0 failed

*** Test Cases ***
Different Variable Files Are Imported Correctly
    [Documentation]    Verifies that it is possible to import different variable
    ...    files even when they have the same name. Verifies that new variables
    ...    are imported, existing overridden, and old ones not visible anymore.
    Check Test Suite    Different Variable Files    ${6 TESTS}

Same Variable File Is Not Re-Imported
    Check Test Case   Importing Same Variable File Does Not Re-Import Module
