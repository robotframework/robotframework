*** Test Cases ***
Test Case With ELSE and ELSE IF
    Run Keyword If    expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation    ELSE IF     expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation    ELSE IF     expression    No Operation    ELSE IF     expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation
    ...    ELSE IF     expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation    ELSE IF     expression    No Operation    ELSE    No Operation    1    2    3    4    5    6
    Run Keyword If
    ...    expression    No Operation    ELSE    No Operation


*** Keywords ***
Keyword With ELSE and ELSE IF
    Run Keyword If    expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation    ELSE IF     expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation    ELSE IF     expression    No Operation    ELSE IF     expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation
    ...    ELSE IF     expression    No Operation    ELSE    No Operation
    Run Keyword If    expression    No Operation    ELSE IF     expression    No Operation    ELSE    No Operation    1    2    3    4    5    6
    Run Keyword If
    ...    expression    No Operation    ELSE    No Operation
