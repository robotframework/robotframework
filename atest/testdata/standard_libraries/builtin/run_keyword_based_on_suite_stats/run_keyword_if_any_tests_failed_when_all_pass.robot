*** Settings ***
Suite Teardown    Run Keyword If Any Tests Failed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated

*** Test Cases ***
Run Keyword If Any Tests failed Is not executed when All Tests Pass
    No Operation
