*** Settings ***
Resource          formats_resource.robot
Suite Setup       Run tests    -F txt:tsv    ${MIXEDDIR}

*** Variables ***
@{TSV TESTS}      TSV Passing     TSV Failing    TXT Resource
@{TXT TESTS}      TXT Passing     TXT Failing    TSV Resource

*** Test Cases ***
TSV Suite With TXT Resource
    Check Test Case    TXT Resource

TXT Suite With TSV Resource
    Check Test Case    TSV Resource

Directory With Mixed Data
    Verify Directory with Mixed Data

*** Keywords ***
Verify Directory With Mixed Data
    Should Be Equal    ${SUITE.name}    Mixed Data
    Should Contain Suites    ${SUITE}    TSV    TXT
    Should Be Equal    ${SUITE.suites[0].doc}    Test suite in TSV file
    Should Be Equal    ${SUITE.suites[1].doc}    Test suite in TXT file
    Should Contain Tests    ${SUITE.suites[0]}    @{TSV TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{TXT TESTS}
