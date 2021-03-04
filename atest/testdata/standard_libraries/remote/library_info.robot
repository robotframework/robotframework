*** Settings ***
Library           Remote    http://127.0.0.1:${PORT}
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
Load large library
    ${ret}=  some keyword
    Should be equal  ${ret}  some
    ${ret}=  keyword 7777
    Should be equal  ${ret}  7777
