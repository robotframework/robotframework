*** Settings ***
Resource        formats_resource.robot

*** Test Cases ***
One TSV
    Run sample file and check tests    ${EMPTY}    ${TSVDIR}/sample.tsv

TSV With TSV Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

TSV Directory
    Run Suite Dir And Check Results    -F tsv    ${TSVDIR}

Directory With TSV Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
