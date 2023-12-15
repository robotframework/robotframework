*** Settings ***
Library        LegacyOutputHelper.py
Resource       atest_resource.robot

*** Test Cases ***
Legacy output with Robot
    Run Tests    --legacyoutput    output/legacy.robot    validate output=False
    Validate output

Legacy output with Rebot
    Run Tests    ${EMPTY}    output/legacy.robot
    Copy Previous Outfile
    Run Rebot    --legacy-output    ${OUTFILE COPY}    validate output=False

*** Keywords ***
Validate output
    Should Contain Tests    ${SUITE}    Passing    Failing    Failing setup
    ...    Failing teardown    Controls    Embedded    Warning
    ${output} =    Mask Changing Parts    ${OUTFILE}
    ${expected} =    Mask Changing Parts    ${DATADIR}/output/legacy.xml
    Elements Should Be Equal    ${output}    ${expected}    sort_children=True
