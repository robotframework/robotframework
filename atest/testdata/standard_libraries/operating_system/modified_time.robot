*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot
Library           ../builtin/times.py

*** Test Cases ***
Get Modified Time As Timestamp
    ${time1} =    Get Modified Time    ${CURDIR}
    Create File    ${TESTFILE}    hello
    ${time2} =    Get Modified Time    ${TESTFILE}
    Should Be True    '${time2}' >= '${time1}'
    Should Match Regexp    ${time1}    \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}

Get Modified Time As Seconds After Epoch
    ${dirtime} =    Get Modified Time    ${CURDIR}    epoch
    Should Be True    ${dirtime} > 0
    ${current} =    Get Time    epoch
    Should Be True    ${current} >= ${dirtime}

Get Modified Time As Parts
    ${year} =    Get Modified Time    ${CURDIR}    year
    Should Match Regexp    ${year}    \\d{4}
    ${yyyy}    ${mm}    ${dd} =    Get Modified Time    ${CURDIR}    year, month, day
    Should Be Equal    ${yyyy}    ${year}
    # Must use `int('x')` because otherwise 08 and 09 are considered octal
    Should Be True    1 <= int('${mm}') <= 12
    Should Be True    1 <= int('${dd}') <= 31
    @{time} =    Get Modified Time    ${CURDIR}    year, sec, min, hour
    Should Be Equal    ${time}[0]    ${year}
    Should Be True    0 <= int('${time}[1]') <= 23
    Should Be True    0 <= int('${time}[2]') <= 59
    Should Be True    0 <= int('${time}[3]') <= 59

Get Modified Time Fails When Path Does Not Exist
    [Documentation]    FAIL Path '${CURDIR}${/}does_not_exist' does not exist.
    Get Modified Time    ${CURDIR}/does_not_exist

Set Modified Time Using Epoch
    [Documentation]    FAIL ValueError: Epoch time must be positive (got -1).
    Create File    ${TESTFILE}
    ${epoch} =    Evaluate    1542892422.0 + time.timezone
    Set Modified Time    ${TESTFILE}    ${epoch}
    ${mtime} =    Get Modified Time    ${TESTFILE}
    Should Be Equal    ${mtime}    2018-11-22 13:13:42
    Set Modified time    ${TESTFILE}    -1

Set Modified Time Using Timestamp
    Create File    ${TESTFILE}
    ${expected} =    Evaluate    1542892422.0 + time.timezone
    FOR    ${timestamp}    IN    2018-11-22 13:13:42    20181122 13:13:42
    ...    20181122 131342    20181122-131342    2018-11-22 13:13:42.456
        Set Modified Time    ${TESTFILE}    ${timestamp}
        ${mtime} =    Get Modified Time    ${TESTFILE}    epoch
        Should Be Equal    ${mtime}    ${expected}
    END

Set Modified Time Using Invalid Timestamp
    [Documentation]    FAIL ValueError: Invalid time format 'invalid time'.
    Create File    ${TESTFILE}
    Set Modified Time    ${TESTFILE}    invalid time

Set Modified Time Using NOW
    Create File    ${TESTFILE}
    ${t0} =    Get Modified Time    ${TESTFILE}    epoch
    Sleep    1.1 seconds
    Set Modified Time    ${TESTFILE}    NOW
    ${t1} =    Get Modified Time    ${TESTFILE}    epoch
    Should Be True    ${t0} < ${t1} < ${t0}+5
    Set Modified Time    ${TESTFILE}    NOW-1day
    ${t2} =    Get Modified Time    ${TESTFILE}    epoch
    Should Be True    ${t2}-4 <= ${t1} - 24*60*60 <= ${t2}
    Set Modified Time    ${TESTFILE}    now + 1 day 2 hour 3 min 4 seconds 10 ms
    ${t3} =    Get Modified Time    ${TESTFILE}    epoch
    Should Be True    ${t3}-9 <= ${t1} + (24*60*60 + 2*60*60 + 3*60 + 4) <= ${t3}

Set Modified Time Using UTC
    Create File    ${TESTFILE}
    ${now} =    Get Time    epoch
    Set Modified Time    ${TESTFILE}    UTC
    ${mtime} =    Get Modified Time    ${TESTFILE}    epoch
    ${zone} =    Get Current Time Zone
    Should Be True    ${now} <= ${mtime} - ${zone} <= ${now} + 2
    Set Modified Time    ${TESTFILE}    utc - ${zone}
    ${mtime} =    Get Modified Time    ${TESTFILE}    epoch
    Should Be True    ${now} <= ${mtime} <= ${now} + 4

Set Modified Time Using NOW + invalid
    [Documentation]    FAIL ValueError: Invalid time string 'invalid'.
    Set Modified Time    ${TESTFILE}    NOW + invalid

Set Modified Time Fails When Path Does Not Exist
    [Documentation]    FAIL File '${CURDIR}${/}does_not_exist' does not exist.
    Set Modified Time    ${CURDIR}/does_not_exist    0

Set Modified Time Fails When Path Is Directory
    [Documentation]    FAIL Path '${CURDIR}' is not a regular file.
    Set Modified Time    ${CURDIR}    0

Set And Get Modified Time Of Non-ASCII File
    Create File    ${NON ASCII}
    Set Modified Time    ${NON ASCII}    2010-09-26 21:22:42
    ${time} =    Get Modified Time    ${NON ASCII}
    Should Be Equal    ${time}    2010-09-26 21:22:42

Set And Get Modified Time Of File With Spaces In Name
    Create File    ${WITH SPACE}
    Set Modified Time    ${WITH SPACE}    2010-09-26 21:24
    ${time} =    Get Modified Time    ${WITH SPACE}
    Should Be Equal    ${time}    2010-09-26 21:24:00

Path as `pathlib.Path`
    Create File    ${BASE}/file.txt
    Set Modified Time    ${PATH/'file.txt'}    2022-09-16 19:41:12
    ${time} =    Get Modified Time    ${PATH/'file.txt'}
    Should Be Equal    ${time}    2022-09-16 19:41:12
