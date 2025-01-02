*** Settings ***
Library           Process

*** Test Cases ***
Get whole result object
    Start Process    python    -c   print("Hello"*32768)
    wait_for_process
    ${result} =    Get Process Result    
    Should Be Equal    ${result.rc}    ${0}

