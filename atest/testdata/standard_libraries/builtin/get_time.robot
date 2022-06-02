*** Settings ***
Library           times.py
Library           DateTime

*** Test Cases ***
Get Time As Timestamp
    ${time1} =    Get Time
    Should Match Regexp    ${time1}    \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}
    ${time2} =    Get Time    give me timestamp, please
    Should Be True    '${time2}' >= '${time1}'

Get Time As Seconds After Epoch
    ${time} =    Get Time    epoch
    Should Be True    0 < ${time}

Get Time As Parts
    @{time} =    Get Time    year, month, day, hour, min, sec
    Should Match Regexp    ${time}[0]    \\d{4}
    Should Be True    1 <= int('${time}[1]') <= 12
    Should Be True    1 <= int('${time}[2]') <= 31
    Should Be True    0 <= int('${time}[3]') <= 23
    Should Be True    0 <= int('${time}[4]') <= 59
    Should Be True    0 <= int('${time}[5]') <= 59
    ${year}    ${min}    ${sec} =    Get Time    seconds and minutes and year and whatnot
    Should Match Regexp    ${year}    \\d{4}
    Should Be True    0 <= int('${min}') <= 59
    Should Be True    0 <= int('${sec}') <= 59

When Time Is Seconds After Epoch
    ${secs after epoch} =    Get Timestamp From Date    2007    4    27    9    14    27
    ${converted date string} =    Get Time    ${EMPTY}    ${secs after epoch}
    Should Be Equal    ${converted date string}    2007-04-27 09:14:27

When Time Is Seconds After Epoch As String
    ${secs after epoch} =    Get Timestamp From Date    2007    4    27    9    14    27
    ${secs after epoch} =    Convert To String    ${secs after epoch}
    ${converted date string} =    Get Time    time_=${secs after epoch}
    Should Be Equal    ${converted date string}    2007-04-27 09:14:27

When Time Is Timestamp
    ${secs} =    Get Time    secs    2007-04-27 09:14:27
    Should Be Equal    ${secs}    27

When Time Is Now
    ${time1} =    Get Time    timestamp    NOW
    Should Match Regexp    ${time1}    \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}
    ${time2} =    Get Time    give me timestamp, please    NOW +1 seconds
    Should Be True    '${time2}' > '${time1}'

When Time Is Now +- Something
    ${time} =    Get Time    epoch    NOW
    ${time minus} =    Get Time    epoch    NOW - 1 hour
    ${time plus} =    Get Time    epoch    NOW + 2 minutes 1 second
    Should Be True    ${time minus} < ${time} < ${time plus}

Empty Format Is Interpreted As Timestamp When Time Given
    ${time} =    Get Time    ${EMPTY}    2007-04-27 09:14:27
    Should Be Equal    ${time}    2007-04-27 09:14:27

Invalid Time Does Not Cause Un-Catchable Failure
    Run Keyword And Expect Error    ValueError: Invalid time format 'invalid'.    Get Time    timestamp    invalid

When Time Is UTC
    ${before} =    Get Time    epoch    NOW
    ${utc} =    Get Time    epoch    UTC
    ${after} =    Get Time    epoch    NOW
    ${zone} =    Get Current Time Zone
    Should Be True    ${before} <= ${utc} - ${zone} <= ${after}

When Time Is UTC +- Something
    ${time} =    Get Time    epoch    UTC
    ${time minus} =    Get Time    epoch    UTC - 1 hour
    ${time plus} =    Get Time    epoch    UTC + 2 minutes 1 second
    Should Be True    ${time minus} < ${time} < ${time plus}

DST is handled correctly when adding or substracting time
    FOR    ${i}    IN    91    183    274
        WHILE    True
            ${now}=      Get Time   time_=now
            ${past}=     Get Time   time_=now - ${i}day
            ${future}=   Get Time   time_=now + ${i}day
            ${now2}=     Get Time   time_=now
            # Make sure seconds did not change between Get Time calls.
            IF    '${now}' == '${now2}'    BREAK
        END
        ${delta}=   Subtract Date From Date   ${now}   ${past}   compact
        Should Be Equal   ${delta}   ${i}d
        ${delta}=   Subtract Date From Date   ${now}   ${future}   compact
        Should Be Equal   ${delta}   - ${i}d
    END
