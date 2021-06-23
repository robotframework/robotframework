*** Settings ***
Resource        formats_resource.robot

*** Test Cases ***
One TXT
    Run sample file and check tests    ${EMPTY}    ${TXTDIR}/sample.txt

TXT With TXT Resource
    Previous Run Should Have Been Successful
    Check Test Case    Resource File

TXT Directory
    Run Suite Dir And Check Results    -FTXT    ${TXTDIR}

Directory With TXT Init
    Previous Run Should Have Been Successful
    Check Suite With Init    ${SUITE.suites[1]}
