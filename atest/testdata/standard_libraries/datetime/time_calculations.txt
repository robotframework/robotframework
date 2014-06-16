*** Settings ***
Library      DateTime
Variables    datesandtimes.py

*** Test Cases ***
Time addition to time should succeed
    [Template]    Time Addition To Time Should Succeed
    01:00:00.000         1 hour      2 hours
    5 hours 3 minutes    4 minutes   05:07:00.000    timer
    5 hours 3 minutes    ${4.0}      05:03:04.000    timer

Time subtraction from time should succeed
    [Template]    Time Subtraction From Time Should Succeed
    02:00:00.000    1 hour    1 hour
    5 hours 3 minutes    4 minutes   04:59:00.000    timer
    5 hours 3 minutes    ${4.0}      05:02:56.000    timer

*** Keywords ***
Time Addition To Time Should Succeed
    [Arguments]    ${time1}    ${time2}    ${expected}    ${result_format}=verbose
    ${new_time} =    Add Time To Time    ${time1}    ${time2}    ${result_format}
    Should Be Equal    ${new_time}    ${expected}

Time Subtraction From Time Should Succeed
    [Arguments]    ${time1}    ${time2}    ${expected}    ${result_format}=verbose
    ${new_time} =    Subtract Time From Time    ${time1}    ${time2}    ${result_format}
    Should Be Equal    ${new_time}    ${expected}
