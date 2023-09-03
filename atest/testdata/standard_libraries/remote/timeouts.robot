*** Settings ***
Library           DateTime

*** Variables ***
${PORT}           8270

*** Test Cases ***
Initial connection failure
    Test initial connection failure

Too long keyword execution time
    Test too long keyword execution time

*** Keywords ***
Test initial connection failure
    # Would be better to test the actual error, but it depends on network
    # configuation etc.
    ${error} =    Catenate
    ...    Getting keyword names from library 'Remote' failed:
    ...    Calling dynamic method 'get_keyword_names' failed:
    ...    Connecting remote server at http://1.2.3.4:666 failed: *
    ${start} =    Get Current Date
    Run Keyword And Expect Error    ${error}
    ...    Import Library    Remote    1.2.3.4:666    timeout=0.2 seconds
    ${end} =    Get Current Date
    ${elapsed} =    Subtract Date From Date    ${end}    ${start}
    Should Be True    ${elapsed} < 10

Test too long keyword execution time
    Import Library           Remote    http://127.0.0.1:${PORT}     ${0.3}
    Run Keyword And Expect Error
    ...    GLOB: Connection to remote server broken:* timed out
    ...    Remote.Sleep    2
