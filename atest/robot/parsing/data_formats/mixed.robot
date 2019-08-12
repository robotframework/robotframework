*** Settings ***
Force Tags        require-docutils
Resource          formats_resource.robot

*** Variables ***
@{TSV TESTS}      TSV Passing     TSV Failing     ReST Resource    TXT Resource
@{REST TESTS}     ReST Passing    ReST Failing    TSV Resource     TXT Resource
@{TXT TESTS}      TXT Passing     TXT Failing     ReST Resource    TSV Resource

*** Test Cases ***
TSV Suite With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    ReST Resource

TSV Suite With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    TXT Resource

ReST Suite With TSV Resource
    Previous Run Should Have Been Successful
    Check Test Case    TSV Resource

ReST Suite With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    TXT Resource

TXT Suite With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    ReST Resource

TXT Suite With TSV Resource
    Previous Run Should Have Been Successful
    Check Test Case    TSV Resource

Directory With Mixed Data
    Run Tests And Verify Status    ${EMPTY}    ${MIXEDDIR}
    Verify Directory with Mixed Data With ReST

Multiple Data Sources Without reST
    Run Tests And Verify Status    ${EMPTY}     ${TSVDIR}/sample.tsv ${TXTDIR}/sample.txt ${MIXEDDIR}
    Verify Multiple Data Sources Without ReST

Multiple Data Sources With reST
    Run Tests And Verify Status    ${EMPTY}     ${TSVDIR}/sample.tsv ${RESTDIR}/sample.rst ${TXTDIR}/sample.txt ${MIXEDDIR}
    Verify Multiple Data Sources With ReST

*** Keywords ***
Verify Directory With Mixed Data With ReST
    Should Be Equal    ${SUITE.name}    Mixed Data
    Should Contain Suites    ${SUITE}    REST    TSV    TXT
    Should Be Equal    ${SUITE.suites[0].doc}    Test suite in ReST file
    Should Be Equal    ${SUITE.suites[1].doc}    Test suite in TSV file
    Should Be Equal    ${SUITE.suites[2].doc}    Test suite in TXT file
    Should Contain Tests    ${SUITE.suites[0]}    @{REST TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{TSV TESTS}
    Should Contain Tests    ${SUITE.suites[2]}    @{TXT TESTS}

Verify Multiple Data Sources With ReST
    Should Be Equal    ${SUITE.name}    Sample & Sample & Sample & Sample & Mixed Data
    Should Contain Suites    ${SUITE}    Sample    Sample    Sample    Sample    Mixed Data
    Should Contain Tests    ${SUITE.suites[0]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[2]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[3]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[4]}    @{REST TESTS}    @{TSV TESTS}    @{TXT TESTS}

Verify Multiple Data Sources Without ReST
    Should Be Equal    ${SUITE.name}    Sample & Sample & Sample & Mixed Data
    Should Contain Suites    ${SUITE}    Sample    Sample    Sample    Mixed Data
    Should Contain Tests    ${SUITE.suites[0]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[2]}    @{SAMPLE_TESTS}
