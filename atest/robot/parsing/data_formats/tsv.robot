*** Settings ***
Resource        formats_resource.robot

*** Test Cases ***
One TSV
    Run sample file and check tests    ${EMPTY}    ${TSVDIR}/sample.tsv

TSV With TSV Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

Un-escaping quoting and empty cells are deprecated
    Previous Run Should Have Been Successful
    Check un-escaping and empty cell deprecations

Parsing TSV files automatically is deprecated
    Previous Run Should Have Been Successful
    Check Automatic Parsing Deprecated Message    2    ${TSVDIR}/sample.tsv
    Length should be    ${ERRORS}    3

Using --extension avoids deprecation warning
    Run sample file and check tests    --extension TsV    ${TSVDIR}/sample.tsv
    Check un-escaping and empty cell deprecations
    Length should be    ${ERRORS}    2

TSV Directory
    Run Suite Dir And Check Results    -F tsv    ${TSVDIR}

Directory With TSV Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}

*** Keywords ***
Check un-escaping and empty cell deprecations
    ${path} =    Normalize Path    ${TSVDIR}/sample.tsv
    Check Log Message    ${ERRORS[0]}
    ...    Un-escaping quotes in TSV files is deprecated. Change cells in '${path}' to not contain surrounding quotes.    WARN
    Check Log Message    ${ERRORS[1]}
    ...    Empty cells in TSV files are deprecated. Escape them with '\${EMPTY}' in '${path}'.    WARN
