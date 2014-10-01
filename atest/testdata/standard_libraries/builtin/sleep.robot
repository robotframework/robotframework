*** Test Cases ***
Sleep
    ${time1} =    Get Time
    Sleep    1.111
    ${time2} =    Get Time
    Sleep    0 hours 0 mins 1 S E C O N D 234 milliseconds
    ${time3} =    Get Time
    Sleep    ${1.1119}
    ${time4} =    Get Time
    Should Be True    '${time4}' > '${time3}' > '${time2}' > '${time1}'

Sleep With Negative Time
    ${start} =    Get Time    epoch
    Sleep    -1
    Sleep    -10 hours
    ${end} =    Get Time    epoch
    Should Be True    ${start} == ${end} or ${start} == ${end} - 1

Sleep With Reason
    Sleep    42 ms    No good reason

Invalid Time Does Not Cause Uncatchable Error
    Run Keyword And Expect Error    ValueError: Invalid time string 'invalid time'.    Sleep    invalid time

Can Stop Sleep With Timeout
    [Documentation]    FAIL Test timeout 10 milliseconds exceeded.
    [Timeout]    10 milliseconds
    Sleep    100 seconds

