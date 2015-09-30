*** Settings ***
Force Tags        require-docutils
Resource          formats_resource.robot

*** Variables ***
@{HTML TESTS}     HTML Passing    HTML Failing    TSV Resource     ReST Resource    TXT Resource
@{TSV TESTS}      TSV Passing     TSV Failing     HTML Resource    ReST Resource    TXT Resource
@{REST TESTS}     ReST Passing    ReST Failing    HTML Resource    TSV Resource     TXT Resource
@{TXT TESTS}      TXT Passing     TXT Failing     HTML Resource    ReST Resource    TSV Resource

*** Test Cases ***
HTML Suite With TSV Resource
    Run Tests And Verify Status    ${MIXEDDIR}/HTML.html
    Check Test Case    TSV Resource

HTML Suite With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    ReST Resource

HTML Suite With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    TXT Resource

TSV Suite With HTML Resource
    Run Tests And Verify Status    ${MIXEDDIR}/TSV.tsv
    Check Test Case    HTML Resource

TSV Suite With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    ReST Resource

TSV Suite With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    TXT Resource

ReST Suite With HTML Resource
    Run Tests And Verify Status    ${MIXEDDIR}/REST.rest
    Check Test Case    HTML Resource

ReST Suite With TSV Resource
    Previous Run Should Have Been Successful
    Check Test Case    TSV Resource

ReST Suite With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    TXT Resource

TXT Suite With HTML Resource
    Run Tests And Verify Status    ${MIXEDDIR}/TXT.txt
    Check Test Case    HTML Resource

TXT Suite With ReST Resource
    Previous Run Should Have Been Successful
    Check Test Case    ReST Resource

TXT Suite With TSV Resource
    Previous Run Should Have Been Successful
    Check Test Case    TSV Resource

Directory With Mixed Data
    Run Tests And Verify Status    ${MIXEDDIR}
    Verify Directory with Mixed Data With ReST

Multiple Data Sources Without reST
    Run Tests And Verify Status    ${HTMLDIR}/sample.html ${TSVDIR}/sample.tsv ${TXTDIR}/sample.txt ${MIXEDDIR}
    Verify Multiple Data Sources Without ReST

Multiple Data Sources With reST
    Run Tests And Verify Status    ${HTMLDIR}/sample.html ${TSVDIR}/sample.tsv ${RESTDIR}/sample.rst ${TXTDIR}/sample.txt ${MIXEDDIR}
    Verify Multiple Data Sources With ReST

*** Keywords ***
Verify Directory With Mixed Data With ReST
    Should Be Equal    ${SUITE.name}    Mixed Data
    Should Contain Suites    ${SUITE}    HTML    REST    TSV    TXT
    Should Be Equal    ${SUITE.suites[0].doc}    Test suite in HTML file
    Should Be Equal    ${SUITE.suites[1].doc}    Test suite in ReST file
    Should Be Equal    ${SUITE.suites[2].doc}    Test suite in TSV file
    Should Be Equal    ${SUITE.suites[3].doc}    Test suite in TXT file
    Should Contain Tests    ${SUITE.suites[0]}    @{HTML TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{REST TESTS}
    Should Contain Tests    ${SUITE.suites[2]}    @{TSV TESTS}
    Should Contain Tests    ${SUITE.suites[3]}    @{TXT TESTS}

Verify Multiple Data Sources With ReST
    Should Be Equal    ${SUITE.name}    Sample & Sample & Sample & Sample & Mixed Data
    Should Contain Suites    ${SUITE}    Sample    Sample    Sample    Sample    Mixed Data
    Should Contain Tests    ${SUITE.suites[0]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[2]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[3]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[4]}    @{HTML TESTS}    @{REST TESTS}    @{TSV TESTS}    @{TXT TESTS}

Verify Multiple Data Sources Without ReST
    Should Be Equal    ${SUITE.name}    Sample & Sample & Sample & Mixed Data
    Should Contain Suites    ${SUITE}    Sample    Sample    Sample    Mixed Data
    Should Contain Tests    ${SUITE.suites[0]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[1]}    @{SAMPLE_TESTS}
    Should Contain Tests    ${SUITE.suites[2]}    @{SAMPLE_TESTS}
