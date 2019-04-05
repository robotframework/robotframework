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
    Check quoting and empty cell deprecations

Parsing TSV files automatically is deprecated
    Previous Run Should Have Been Successful
    Check Automatic Parsing Deprecated Message    6    ${TSVDIR}/sample.tsv
    Length should be    ${ERRORS}    7

Using --extension avoids deprecation warning
    Run sample file and check tests    --extension TsV    ${TSVDIR}/sample.tsv
    Check quoting and empty cell deprecations
    Length should be    ${ERRORS}    6

TSV Directory
    Run Suite Dir And Check Results    -F tsv    ${TSVDIR}

Directory With TSV Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}

*** Keywords ***
Check quoting and empty cell deprecations
    ${path} =    Normalize Path    ${TSVDIR}/sample.tsv
    Check quoting deprecation    ${ERRORS[0]}    ${path}    1
    ...    "This text should be ignored, even though it's not a comment."
    Check quoting deprecation    ${ERRORS[1]}    ${path}    20
    ...    """this has """"many "" quotes """""
    Check quoting deprecation    ${ERRORS[2]}    ${path}    51
    ...    "Hello, world!!"
    Check quoting deprecation    ${ERRORS[3]}    ${path}    93
    ...    """this has """"many "" quotes """""
    Check empty cell deprecation    ${ERRORS[4]}    ${path}    97
    Check empty cell deprecation    ${ERRORS[5]}    ${path}    98

Check quoting deprecation
    [Arguments]    ${error}    ${path}    ${line}    ${problem}
    ${msg} =    Catenate
    ...    TSV file '${path}' has quotes around cells which is deprecated and must be fixed.
    ...    Remove quotes from '${problem}' on line ${line}.
    Check Log Message    ${error}    ${msg}    WARN

Check empty cell deprecation
    [Arguments]    ${error}    ${path}    ${line}
    ${msg} =    Catenate
    ...    TSV file '${path}' has empty data cells which is deprecated and must be fixed.
    ...    Escape empty cells on line ${line} with '\${EMPTY}'.
    Check Log Message    ${error}    ${msg}    WARN
