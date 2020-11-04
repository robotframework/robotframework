*** Settings ***
Documentation    Created for testing if / else with listeners

*** Test Cases ***
If structure
    IF  ${False}
        Fail  not going here
    ELSE IF  ${True}
        Log   else if branch
    ELSE
        Fail  not going here
    END
