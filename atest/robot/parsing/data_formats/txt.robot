*** Settings ***
Resource        formats_resource.robot

*** Test Cases ***
One TXT
    Run sample file and check tests    ${EMPTY}    ${TXTDIR}/sample.txt

TXT With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

Parsing TXT files automatically is deprecated
    Previous Run Should Have Been Successful
    Check Automatic Parsing Deprecated Message    0    ${TXTDIR}/sample.txt
    Length should be    ${ERRORS}    1

Using --extension avoids deprecation warning
    Run sample file and check tests    --extension txt    ${TXTDIR}/sample.txt
    Should be empty    ${ERRORS}

TXT Directory
    Run Suite Dir And Check Results    -FTXT    ${TXTDIR}

Directory With TXT Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
