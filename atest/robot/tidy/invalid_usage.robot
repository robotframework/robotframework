*** Settings ***
Test Template      Tidy run should fail
Resource           tidy_resource.robot

*** Test Cases ***
Too few arguments
    Expected at least 1 argument, got 0.

Invalid option
    option --nonex not recognized     --nonex

Non-existing input
    Default mode requires input to be a file.        ${EMPTY}       nonex.robot
    --inplace requires inputs to be files.           --inplace      nonex.robot
    --recursive requires input to be a directory.    --recursive    nonex

Invalid output
    [Setup]    Create Directory    ${OUTFILE}
    Opening Tidy output file '${OUTFILE}' failed: *Error: *
    ...    input=golden.robot    output=${OUTFILE}
    [Teardown]    Remove Directory    ${OUTFILE}

*** Keywords ***
Tidy run should fail
    [Arguments]    ${error}    @{args}    &{kwargs}
    ${output} =    Run Tidy    @{args}    &{kwargs}    rc=252    deprecation=False
    Should Match    ${output}    ${error}${USAGE TIP}
