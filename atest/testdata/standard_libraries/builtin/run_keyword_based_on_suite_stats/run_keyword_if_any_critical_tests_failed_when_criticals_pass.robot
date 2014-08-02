*** Setting ***
Suite Teardown    Run Keyword If Any Critical Tests Failed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated
Default Tags      critical

*** Test Case ***
Run Keyword If Any Critical Tests failed Is not executed when All Critcal Tests Pass
    No Operation
